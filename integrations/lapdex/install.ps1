$ErrorActionPreference = 'Stop'
$exitCode = 1
try {
    $cli = Get-Command lapdex -CommandType Application -ErrorAction SilentlyContinue
    if (-not $cli) {
        throw '未找到 Lapdex CLI。请先安装 CLI，并确保 lapdex 命令在 PATH 中。'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'SKILL.md') -PathType Leaf) -or
        -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'bundle-manifest.json') -PathType Leaf)) {
        throw '请完整解压技能包，再从 laco-laoshifu 目录运行安装脚本。'
    }

    $queryFile = [IO.Path]::GetTempFileName()
    try {
        $prompt = @"
安装路径「$PSScriptRoot」下的 skill。
请将该完整目录作为 laco-laoshifu 安装到当前 Lapdex profile 的用户技能目录，保留 SKILL.md 和 references 的相对位置。若已有同名安装，请停止并报告路径，以便用户备份。安装后检查目标的 SKILL.md 和 references/kd/source/README.md，并报告实际结果和目标路径。
"@
        [IO.File]::WriteAllText($queryFile, $prompt, [Text.UTF8Encoding]::new($false))
        & $cli.Source chat --oneshot --query-file $queryFile
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq 0) {
            Write-Host 'Lapdex CLI 已退出。请查看上方安装结果，并在 Lapdex 技能列表中确认。'
        }
    } finally {
        Remove-Item -LiteralPath $queryFile -ErrorAction SilentlyContinue
    }
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
}
exit $exitCode
