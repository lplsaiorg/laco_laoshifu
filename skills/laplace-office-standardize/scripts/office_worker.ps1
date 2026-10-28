param(
    [Parameter(Mandatory=$true)][string]$JobPath,
    [Parameter(Mandatory=$true)][string]$ResultPath
)
$ErrorActionPreference = 'Stop'
$job = Get-Content -LiteralPath $JobPath -Raw -Encoding UTF8 | ConvertFrom-Json
$cfg = $job.profile
$script:notes = [Collections.Generic.List[string]]::new()
$script:app = $null
$script:doc = $null
$script:owned = $false
$script:savedSettings = @{}
$script:wordUpdateLinks = $null
$logoTag = 'LaplaceDocs.CompanyLogo'

function Color-Value([string]$hexColor) {
    $h = $hexColor.TrimStart('#')
    return [Convert]::ToInt32($h.Substring(0,2),16) + 256 * [Convert]::ToInt32($h.Substring(2,2),16) + 65536 * [Convert]::ToInt32($h.Substring(4,2),16)
}
function Hash-Text([string]$value) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algorithm.ComputeHash([Text.Encoding]::UTF8.GetBytes($value))).Replace('-','') }
    finally { $algorithm.Dispose() }
}
function Open-Office([string]$progId, [string]$processName) {
    $before = @(Get-Process -Name $processName -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
    $script:app = New-Object -ComObject $progId
    if (-not ('LaplaceDocs.NativeWindow' -as [type])) {
        Add-Type -TypeDefinition 'namespace LaplaceDocs { public static class NativeWindow { [System.Runtime.InteropServices.DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(System.IntPtr hwnd, out uint processId); } }'
    }
    [uint32]$officeProcessId = 0
    $windowHandle = $null
    try { $windowHandle = $script:app.Hwnd } catch {}
    if ($null -ne $windowHandle -and $windowHandle -ne 0) {
        [void][LaplaceDocs.NativeWindow]::GetWindowThreadProcessId([IntPtr]$windowHandle, [ref]$officeProcessId)
    }
    $newProcesses = @(Get-Process -Name $processName -ErrorAction SilentlyContinue | Where-Object { $before -notcontains $_.Id })
    $script:owned = ($officeProcessId -ne 0 -and $before -notcontains [int]$officeProcessId) -or ($officeProcessId -eq 0 -and $newProcesses.Count -eq 1)
    foreach ($key in @('DisplayAlerts','AutomationSecurity','ScreenUpdating','EnableEvents','Calculation')) {
        try { $script:savedSettings[$key] = $script:app.$key } catch {}
    }
    try { $script:app.AutomationSecurity = 3 } catch {}
    try { $script:app.DisplayAlerts = 0 } catch {}
    try { $script:app.ScreenUpdating = $false } catch {}
    try { $script:app.EnableEvents = $false } catch {}
    if ($progId -eq 'Word.Application') {
        $script:wordUpdateLinks = $script:app.Options.UpdateLinksAtOpen
        $script:app.Options.UpdateLinksAtOpen = $false
    }
    if ($progId -eq 'Excel.Application') { try { $script:app.Calculation = -4135 } catch {} }
    if ($script:owned -and $progId -ne 'PowerPoint.Application') { $script:app.Visible = $false }
}
function Font-Word($font, [double]$size) {
    $font.Name = [string]$cfg.font
    $font.NameFarEast = [string]$cfg.font
    $font.Size = $size
}
function Set-Word-Styles($document) {
    $styles = @(@(-1, [double]$cfg.word.body_size_pt), @(-63, [double]$cfg.word.title_size_pt),
        @(-2, [double]$cfg.word.heading_sizes_pt[0]), @(-3, [double]$cfg.word.heading_sizes_pt[1]),
        @(-4, [double]$cfg.word.heading_sizes_pt[2]))
    foreach ($item in $styles) {
        $style = $document.Styles.Item([int]$item[0])
        Font-Word $style.Font $item[1]
        $style.Font.Color = 0
        $style.ParagraphFormat.SpaceAfter = [double]$cfg.word.paragraph_after_pt
        $style.ParagraphFormat.LineSpacingRule = 5
        $style.ParagraphFormat.LineSpacing = 12 * [double]$cfg.word.line_spacing_multiple
        if ($item[0] -ne -1) { $style.Font.Bold = -1; $style.ParagraphFormat.KeepWithNext = -1 }
    }
}
function Brand-Word($document) {
    # Remove only our own legacy body anchors before placing true header objects.
    for ($i = $document.Shapes.Count; $i -ge 1; $i--) {
        if ($document.Shapes.Item($i).AlternativeText -eq $logoTag) { $document.Shapes.Item($i).Delete() }
    }
    # Word exposes a shared header/footer Shapes collection. Clean before adding
    # any new objects, otherwise a later header can delete an earlier header's logo.
    foreach ($section in $document.Sections) {
        foreach ($header in $section.Headers) {
            for ($i = $header.Shapes.Count; $i -ge 1; $i--) {
                if ($header.Shapes.Item($i).AlternativeText -eq $logoTag) { $header.Shapes.Item($i).Delete() }
            }
        }
    }
    $brandedStories = [Collections.Generic.HashSet[string]]::new()
    foreach ($section in $document.Sections) {
        $margin = [double]$cfg.word.margin_mm * 72 / 25.4
        foreach ($side in @('TopMargin','BottomMargin','LeftMargin','RightMargin')) { $section.PageSetup.$side = $margin }
        $section.PageSetup.HeaderDistance = 12
        $headerTypes = [Collections.Generic.List[int]]::new()
        $headerTypes.Add(1)
        if ($section.PageSetup.DifferentFirstPageHeaderFooter) { $headerTypes.Add(2) }
        if ($section.PageSetup.OddAndEvenPagesHeaderFooter) { $headerTypes.Add(3) }
        foreach ($headerType in $headerTypes) {
            $header = $section.Headers.Item($headerType)
            $effectiveSection = [int]$section.Index
            while ($effectiveSection -gt 1 -and $document.Sections.Item($effectiveSection).Headers.Item($headerType).LinkToPrevious) { $effectiveSection-- }
            $storyKey = [string]$effectiveSection + ':' + [string]$headerType
            if (-not $brandedStories.Add($storyKey)) { continue }
            $header.Exists = -1
            $logoHeight = [double]$cfg.logo_width_pt * [double]$job.logo_height / [double]$job.logo_width
            $logo = $header.Shapes.AddPicture([string]$cfg.logo, $false, $true, 0, 0, [double]$cfg.logo_width_pt, $logoHeight, $header.Range)
            $logo.AlternativeText = $logoTag
            $logo.LockAspectRatio = -1
            $logo.Width = [double]$cfg.logo_width_pt
            $logo.RelativeHorizontalPosition = 0
            $logo.Left = -999996
            $logo.RelativeVerticalPosition = 2
            $logo.Top = 0
            $logo.WrapFormat.Type = 3
        }
    }
}
function Format-Word($document, [bool]$creating) {
    if ($creating) { Set-Word-Styles $document }
    elseif ($cfg.word.template) {
        $document.CopyStylesFromTemplate([string]$cfg.word.template)
    }
    else { Set-Word-Styles $document }
    foreach ($paragraph in $document.Paragraphs) {
        if ($paragraph.Range.OMaths.Count -gt 0 -or $paragraph.Range.Font.Name -match '^(Symbol|Wingdings|Webdings)') {
            $script:notes.Add('Word equation/symbol paragraph retained for visual review.')
            continue
        }
        $style = $paragraph.Range.Style
        $fontName = [string]$style.Font.Name
        if ($fontName) { $paragraph.Range.Font.Name = $fontName; $paragraph.Range.Font.NameFarEast = $fontName }
        $size = [double]$style.Font.Size
        if ($size -gt 0 -and $size -lt 200) { $paragraph.Range.Font.Size = $size }
    }
    Brand-Word $document
}
function Excel-Content($workbook) {
    $lines = [Collections.Generic.List[string]]::new()
    foreach ($sheet in $workbook.Worksheets) {
        $used = $sheet.UsedRange
        # Formula includes constants as their original Variant values and preserves formulas.
        $lines.Add($sheet.Name + ':' + $used.Address() + ':' + (ConvertTo-Json -InputObject $used.Formula -Depth 8 -Compress))
    }
    return Hash-Text ($lines -join "`n")
}
function Brand-Excel($sheet, $used) {
    for ($i = $sheet.Shapes.Count; $i -ge 1; $i--) {
        if ($sheet.Shapes.Item($i).AlternativeText -eq $logoTag) { $sheet.Shapes.Item($i).Delete() }
    }
    if ($cfg.excel.sheet_logo) {
        $logo = $sheet.Shapes.AddPicture([string]$cfg.logo, 0, -1, [double]($used.Left + $used.Width + 12), [double]$used.Top, -1, -1)
        $logo.AlternativeText = $logoTag
        $logo.LockAspectRatio = 0
        $logo.Width = [double]$cfg.logo_width_pt
        $logo.Height = [double]$cfg.logo_width_pt * [double]$job.logo_height / [double]$job.logo_width
        $logo.LockAspectRatio = -1
        $logo.Placement = 3
        $logo.DrawingObject.PrintObject = $false
    }
    if ($cfg.excel.print_logo) {
        $sheet.PageSetup.RightHeaderPicture.Filename = [string]$cfg.logo
        $sheet.PageSetup.RightHeaderPicture.Width = [double]$cfg.logo_width_pt
        $sheet.PageSetup.RightHeaderPicture.Height = [double]$cfg.logo_width_pt * [double]$job.logo_height / [double]$job.logo_width
        $sheet.PageSetup.RightHeader = '&G'
        $sheet.PageSetup.TopMargin = 48
        $sheet.PageSetup.HeaderMargin = 8
    }
}
function Format-Excel($workbook, $template) {
    foreach ($sheet in $workbook.Worksheets) {
        if ($sheet.ProtectContents) { throw "Protected worksheet: $($sheet.Name)" }
        $used = $sheet.UsedRange
        $used.Font.Name = [string]$cfg.font
        $used.Font.Size = [double]$cfg.excel.body_size_pt
        $headerRow = [int]$cfg.excel.header_row
        if ($headerRow -ge $used.Row -and $headerRow -lt ($used.Row + $used.Rows.Count)) {
            $header = $sheet.Range($sheet.Cells.Item($headerRow,$used.Column),$sheet.Cells.Item($headerRow,($used.Column + $used.Columns.Count - 1)))
            $header.Font.Bold = $true
            $header.Font.Color = 0
            $header.Interior.Color = Color-Value $cfg.accent_color
            $header.WrapText = $true
            $header.VerticalAlignment = -4108
            if ($null -ne $template) {
                $refSheet = $template.Worksheets.Item(1)
                try { $refSheet = $template.Worksheets.Item($sheet.Name) } catch {}
                $used.Font.Name = $refSheet.Range('A2').Font.Name
                $used.Font.Size = $refSheet.Range('A2').Font.Size
                $header.Font.Name = $refSheet.Range('A1').Font.Name
                $header.Font.Size = $refSheet.Range('A1').Font.Size
                $header.Font.Color = [int]$refSheet.Range('A1').Font.Color
                $header.Interior.Color = [int]$refSheet.Range('A1').Interior.Color
            }
        }
        if ([double]$used.Cells.CountLarge -le [double]$cfg.excel.autofit_max_cells) {
            [void]$used.Columns.AutoFit()
            foreach ($column in $used.Columns) {
                if ($column.ColumnWidth -gt [double]$cfg.excel.max_column_width) {
                    $column.ColumnWidth = [double]$cfg.excel.max_column_width
                    $column.WrapText = $true
                }
            }
            [void]$used.Rows.AutoFit()
        } else { $script:notes.Add("Large worksheet: font/header/logo applied; AutoFit skipped: $($sheet.Name)") }
        foreach ($chartObject in $sheet.ChartObjects()) {
            $chartObject.Chart.ChartArea.Font.Name = [string]$cfg.font
        }
        Brand-Excel $sheet $used
    }
    $script:notes.Add('Excel: values, formulas, number formats and worksheet structure retained; template contributes body/header styles. Screen logo is outside the used cell range; print logo is in the right header.')
}
function Shape-Text($shape) {
    $texts = [Collections.Generic.List[string]]::new()
    if ($shape.Type -eq 6) { foreach ($item in $shape.GroupItems) { $texts.Add((Shape-Text $item)) } }
    elseif ($shape.HasTextFrame -and $shape.TextFrame.HasText) { $texts.Add([string]$shape.TextFrame.TextRange.Text) }
    if ($shape.HasTable) {
        foreach ($row in $shape.Table.Rows) { foreach ($cell in $row.Cells) { $texts.Add([string]$cell.Shape.TextFrame.TextRange.Text) } }
    }
    return ($texts -join "`u{001E}")
}
function Ppt-Content($presentation) {
    $texts = [Collections.Generic.List[string]]::new()
    foreach ($slide in $presentation.Slides) {
        $texts.Add('SLIDE:' + $slide.SlideIndex)
        foreach ($shape in $slide.Shapes) { if ($shape.AlternativeText -ne $logoTag) { $texts.Add((Shape-Text $shape)) } }
    }
    return Hash-Text ($texts -join "`n")
}
function Format-Ppt-Shape($shape) {
    if ($shape.Type -eq 6) { foreach ($item in $shape.GroupItems) { Format-Ppt-Shape $item }; return }
    if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
        $range = $shape.TextFrame.TextRange
        $range.Font.Name = [string]$cfg.font
        $range.Font.NameFarEast = [string]$cfg.font
        if ($shape.Type -eq 14) {
            $placeholderType = $shape.PlaceholderFormat.Type
            if ($placeholderType -in @(1,3)) { $range.Font.Size = [double]$cfg.powerpoint.title_size_pt }
            elseif ($placeholderType -in @(2,4,7)) { $range.Font.Size = [double]$cfg.powerpoint.body_size_pt }
        }
        if ($range.Font.Size -gt 0 -and $range.Font.Size -lt [double]$cfg.powerpoint.minimum_text_pt) {
            $script:notes.Add('PowerPoint contains small source text; inspect readability in the output.')
        }
    }
    if ($shape.HasTable) {
        foreach ($row in $shape.Table.Rows) { foreach ($cell in $row.Cells) { $cell.Shape.TextFrame.TextRange.Font.Name = [string]$cfg.font } }
    }
}
function Format-Ppt($presentation, [bool]$creating) {
    $oldWidth = $presentation.PageSetup.SlideWidth
    $oldHeight = $presentation.PageSetup.SlideHeight
    if (-not $creating -and $cfg.powerpoint.template) { $presentation.ApplyTemplate([string]$cfg.powerpoint.template) }
    # Preserve the source canvas so template application cannot silently resize evidence.
    $presentation.PageSetup.SlideWidth = $oldWidth
    $presentation.PageSetup.SlideHeight = $oldHeight
    foreach ($slide in $presentation.Slides) {
        for ($i = $slide.Shapes.Count; $i -ge 1; $i--) {
            if ($slide.Shapes.Item($i).AlternativeText -eq $logoTag) { $slide.Shapes.Item($i).Delete() }
        }
        foreach ($shape in $slide.Shapes) { Format-Ppt-Shape $shape }
        $w = [double]$cfg.logo_width_pt
        $h = $w * [double]$job.logo_height / [double]$job.logo_width
        $m = [double]$cfg.powerpoint.logo_margin_pt
        $left = [double]$presentation.PageSetup.SlideWidth - $w - $m
        $top = [double]$presentation.PageSetup.SlideHeight - $h - $m
        foreach ($shape in $slide.Shapes) {
            if ($shape.Left -lt $left+$w -and $shape.Left+$shape.Width -gt $left -and $shape.Top -lt $top+$h -and $shape.Top+$shape.Height -gt $top) {
                $script:notes.Add("Logo region overlaps a shape bounding box on slide $($slide.SlideIndex); visual review required.")
            }
        }
        $logo = $slide.Shapes.AddPicture([string]$cfg.logo,0,-1,$left,$top,-1,-1)
        $logo.AlternativeText = $logoTag
        $logo.LockAspectRatio = 0
        $logo.Width = $w
        $logo.Height = $h
        $logo.LockAspectRatio = -1
    }
}

$result = @{ success=$false; content_unchanged=$false; notes=@(); error=$null }
$templateWorkbook = $null
try {
    $creating = $job.mode -eq 'template'
    switch ($job.format) {
        'word' {
            Open-Office 'Word.Application' 'WINWORD'
            if ($creating) {
                $script:doc = $script:app.Documents.Add()
                $script:doc.Content.Text = "拉普拉斯技术文档`r文档标题`r1 目的与范围`r填写本文件的用途、对象和适用范围。`r2 专业内容`r填写经过核实的技术内容、参数单位及出处。`r"
                $script:doc.Paragraphs.Item(1).Style = -63
                $script:doc.Paragraphs.Item(3).Style = -2
                $script:doc.Paragraphs.Item(5).Style = -2
            } else { $script:doc = $script:app.Documents.Open([string]$job.path,$false,$false,$false) }
            if ($script:doc.ProtectionType -ne -1) { throw 'Protected Word document.' }
            $before = Hash-Text ([string]$script:doc.Content.Text)
            Format-Word $script:doc $creating
            $result.content_unchanged = $before -eq (Hash-Text ([string]$script:doc.Content.Text))
            if (-not $result.content_unchanged) { throw 'Word body content changed.' }
            if ($creating) { $script:doc.SaveAs2([string]$job.path,14) } else { $script:doc.Save() }
            if ($job.pdf) { $script:doc.ExportAsFixedFormat([string]$job.pdf,17) }
        }
        'excel' {
            Open-Office 'Excel.Application' 'EXCEL'
            if ($creating) {
                $script:doc = $script:app.Workbooks.Add()
                $sheet = $script:doc.Worksheets.Item(1)
                $sheet.Name = '标准表格'
                $sheet.Range('A1').Value2 = '项目'
                $sheet.Range('B1').Value2 = '数量'
                $sheet.Range('C1').Value2 = '说明'
                $sheet.Range('A2').Value2 = '示例'
                $sheet.Range('B2').Value2 = 1.0
                $sheet.Range('C2').Value2 = '以实际数据替换示例'
            } else { $script:doc = $script:app.Workbooks.Open([string]$job.path,0,$false,5,'','',$true) }
            $before = Excel-Content $script:doc
            if (-not $creating -and $cfg.excel.template) { $templateWorkbook = $script:app.Workbooks.Open([string]$cfg.excel.template,0,$true) }
            Format-Excel $script:doc $templateWorkbook
            $result.content_unchanged = $before -eq (Excel-Content $script:doc)
            if (-not $result.content_unchanged) { throw 'Excel values, formulas or used ranges changed.' }
            if ($creating) { $script:doc.SaveAs([string]$job.path,54) } else { $script:doc.Save() }
            if ($job.pdf) { $script:doc.ExportAsFixedFormat(0,[string]$job.pdf) }
        }
        'powerpoint' {
            Open-Office 'PowerPoint.Application' 'POWERPNT'
            if ($creating) {
                $script:doc = $script:app.Presentations.Add(0)
                $script:doc.PageSetup.SlideWidth = [double]$cfg.powerpoint.template_width_pt
                $script:doc.PageSetup.SlideHeight = [double]$cfg.powerpoint.template_height_pt
                $cover = $script:doc.Slides.Add(1,1)
                $cover.Shapes.Title.TextFrame.TextRange.Text = '拉普拉斯演示文稿'
                $cover.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = '填写主题、部门与版本'
                $body = $script:doc.Slides.Add(2,2)
                $body.Shapes.Title.TextFrame.TextRange.Text = '内容页标题'
                $body.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "说明主题与结论`r保留数据、图表和证据出处"
                $script:doc.SlideMaster.Background.Fill.ForeColor.RGB = 16777215
            } else { $script:doc = $script:app.Presentations.Open([string]$job.path,0,0,0) }
            $before = Ppt-Content $script:doc
            Format-Ppt $script:doc $creating
            $result.content_unchanged = $before -eq (Ppt-Content $script:doc)
            if (-not $result.content_unchanged) { throw 'PowerPoint slide text changed.' }
            if ($creating) { $script:doc.SaveAs([string]$job.path,26) } else { $script:doc.Save() }
            if ($job.pdf) { $script:doc.SaveAs([string]$job.pdf,32) }
        }
        default { throw 'Unknown Office format.' }
    }
    $result.success = $true
} catch { $result.error = $_.Exception.Message; $result.error_location = $_.ScriptStackTrace }
finally {
    if ($null -ne $templateWorkbook) { try { $templateWorkbook.Close($false) } catch {} }
    if ($null -ne $script:doc) {
        try { if ($job.format -eq 'word') { $script:doc.Close(0) } elseif ($job.format -eq 'excel') { $script:doc.Close($false) } else { $script:doc.Saved = -1; $script:doc.Close() } } catch {}
    }
    if ($null -ne $script:app) {
        if ($null -ne $script:wordUpdateLinks) { try { $script:app.Options.UpdateLinksAtOpen = $script:wordUpdateLinks } catch {} }
        foreach ($key in $script:savedSettings.Keys) { try { $script:app.$key = $script:savedSettings[$key] } catch {} }
        if ($script:owned) { try { $script:app.Quit() } catch {} }
    }
    $result.notes = @($script:notes | Select-Object -Unique)
    $result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $ResultPath -Encoding utf8
}
if (-not $result.success) { exit 1 }
