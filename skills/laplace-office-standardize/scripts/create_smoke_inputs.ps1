param([Parameter(Mandatory=$true)][string]$OutputDirectory)
# Integration fixtures only. No existing user documents are opened or modified.
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Fixture directory must be new.' }
New-Item -ItemType Directory -Path $OutputDirectory | Out-Null
$templateRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\assets\templates'))
$word = $null; $excel = $null; $ppt = $null
$document = $null; $workbook = $null; $presentation = $null
$pptBefore = @(Get-Process -Name POWERPNT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false; $word.DisplayAlerts = 0
    $document = $word.Documents.Add((Join-Path $templateRoot 'word.dotx'))
    $document.Content.Text = "管式设备技术说明`r1 说明范围`r本示例包含中文、English、温度 610 ℃、压力 10 Pa。`r2 数据口径`r参考值与现场判定要求分别记录。`r"
    $document.Paragraphs.Item(1).Style = -63
    $document.Paragraphs.Item(2).Style = -2
    $document.Paragraphs.Item(4).Style = -2
    $document.Content.Font.Name = '宋体'; $document.Content.Font.Size = 13
    foreach ($section in $document.Sections) { foreach ($header in $section.Headers) { for ($i=$header.Shapes.Count;$i -ge 1;$i--) { $header.Shapes.Item($i).Delete() } } }
    $document.SaveAs2((Join-Path $OutputDirectory 'technical-note.docx'),16)
    $document.Close(0); $document=$null

    $excel = New-Object -ComObject Excel.Application
    $excel.Visible=$false; $excel.DisplayAlerts=$false
    $workbook = $excel.Workbooks.Add()
    $sheet=$workbook.Worksheets.Item(1); $sheet.Name='检测记录'
    $sheet.Range('A1').Value2='项目'; $sheet.Range('B1').Value2='数量'; $sheet.Range('C1').Value2='单价'; $sheet.Range('D1').Value2='金额'
    $sheet.Range('A2').Value2='样本A'; $sheet.Range('B2').Value2=2.0; $sheet.Range('C2').Value2=125.5; $sheet.Range('D2').Formula='=B2*C2'
    $sheet.Range('A3').Value2='样本B'; $sheet.Range('B3').Value2=0.0; $sheet.Range('C3').Value2=500.0; $sheet.Range('D3').Formula='=B3*C3'
    $sheet.Range('C2:D3').NumberFormat='0.00'
    $sheet.Range('A1:D3').Font.Name='宋体'; $sheet.Range('A1:D3').Font.Size=13
    $chart=$sheet.ChartObjects().Add(20,110,330,180)
    $chart.Chart.SetSourceData($sheet.Range('A1:B3'))
    $workbook.SaveAs((Join-Path $OutputDirectory 'measurement-record.xlsx'),51)
    $workbook.Close($false); $workbook=$null

    $ppt = New-Object -ComObject PowerPoint.Application
    $presentation = $ppt.Presentations.Add(0)
    $presentation.PageSetup.SlideWidth=960; $presentation.PageSetup.SlideHeight=540
    $slide=$presentation.Slides.Add(1,2)
    $slide.Shapes.Title.TextFrame.TextRange.Text='管式设备分析说明'
    $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text="对齐工序与配方版本`r保留温度、压力及计量单位`r记录依据与待确认事项"
    $slide.Shapes.Title.TextFrame.TextRange.Font.Name='宋体'
    $presentation.SaveAs((Join-Path $OutputDirectory 'equipment-overview.pptx'),24)
    $presentation.Close(); $presentation=$null
} finally {
    if ($null -ne $document) { try { $document.Close(0) } catch {} }
    if ($null -ne $workbook) { try { $workbook.Close($false) } catch {} }
    if ($null -ne $presentation) { try { $presentation.Saved=-1; $presentation.Close() } catch {} }
    if ($null -ne $word) { try { $word.Quit() } catch {} }
    if ($null -ne $excel) { try { $excel.Quit() } catch {} }
    if ($null -ne $ppt -and $pptBefore.Count -eq 0) { try { $ppt.Quit() } catch {} }
}
Write-Output $OutputDirectory
