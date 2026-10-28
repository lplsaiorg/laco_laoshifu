# Read-only PDF exports of the dedicated README example inputs.
$ErrorActionPreference = 'Stop'
$exampleRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\examples\office\before'))
$word = $null; $excel = $null; $ppt = $null
$document = $null; $workbook = $null; $presentation = $null
$pptBefore = @(Get-Process -Name POWERPNT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
try {
    if (-not (Test-Path -LiteralPath (Join-Path $exampleRoot 'technical-note.before.pdf'))) {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false; $word.DisplayAlerts = 0
    $document = $word.Documents.Open((Join-Path $exampleRoot 'technical-note.docx'),$false,$true)
    $document.ExportAsFixedFormat((Join-Path $exampleRoot 'technical-note.before.pdf'),17)
    $document.Close(0); $document = $null
    try { $word.Quit() } catch { }; $word = $null
    }

    if (-not (Test-Path -LiteralPath (Join-Path $exampleRoot 'measurement-record.before.pdf'))) {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false; $excel.DisplayAlerts = $false
    $workbook = $excel.Workbooks.Open((Join-Path $exampleRoot 'measurement-record.xlsx'),0,$true)
    $workbook.ExportAsFixedFormat(0,(Join-Path $exampleRoot 'measurement-record.before.pdf'))
    $workbook.Close($false); $workbook = $null
    try { $excel.Quit() } catch { }; $excel = $null
    }

    if (-not (Test-Path -LiteralPath (Join-Path $exampleRoot 'equipment-overview.before.pdf'))) {
    $ppt = New-Object -ComObject PowerPoint.Application
    $presentation = $ppt.Presentations.Open((Join-Path $exampleRoot 'equipment-overview.pptx'),-1,0,0)
    $presentation.SaveAs((Join-Path $exampleRoot 'equipment-overview.before.pdf'),32)
    $presentation.Close(); $presentation = $null
    if ($pptBefore.Count -eq 0) { try { $ppt.Quit() } catch { } }
    $ppt = $null
    }
} finally {
    if ($null -ne $document) { try { $document.Close(0) } catch {} }
    if ($null -ne $workbook) { try { $workbook.Close($false) } catch {} }
    if ($null -ne $presentation) { try { $presentation.Saved=-1; $presentation.Close() } catch {} }
    if ($null -ne $word) { try { $word.Quit() } catch {} }
    if ($null -ne $excel) { try { $excel.Quit() } catch {} }
    if ($null -ne $ppt -and $pptBefore.Count -eq 0) { try { $ppt.Quit() } catch {} }
}
Write-Output "Original example PDF exports are present; existing exports were retained."
