import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('loom/fabric/dashboard_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

missing = [
    'fetchTaskManagerSnap',
    'triggerBlindspotScan',
    'querySubconsciousIntuition',
    'administerTabCompound',
    'fetchRecentTraces',
    'fetchSimulationTelemetry',
    'mintComputeTokens',
    'runDrugSimulation',
    'fetchCommFeed',
    'fetchPharmacopeia',
    'filterCommChannel',
    'administerSelectedToSI',
    'runSimScenario',
    'runBayesianForecast',
    'sendCommMessage',
    'runSubconsciousIncubate',
    'synthesizeNovelCompound',
    'triggerSubconsciousEpiphany',
    'verifyTraceMerkle'
]

for m in missing:
    for i, line in enumerate(lines):
        if m in line and ('<' in line or 'onclick' in line or 'onchange' in line):
            print(f"[{m}] Line {i+1}: {line.strip()[:100]}")
