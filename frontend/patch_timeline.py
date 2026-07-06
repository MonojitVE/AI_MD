import os

def patch_alerts_timeline():
    path = r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\pages\Alerts.jsx"
    with open(path, "r") as f:
        content = f.read()

    # Import TimelineModal
    import_target = "import ResolveAlertModal from '../components/ui/ResolveAlertModal';"
    import_replacement = "import ResolveAlertModal from '../components/ui/ResolveAlertModal';\nimport TimelineModal from '../components/ui/TimelineModal';"
    content = content.replace(import_target, import_replacement)

    # State variable
    state_target = "const [resolvingAlertId, setResolvingAlertId] = useState(null);"
    state_replacement = "const [resolvingAlertId, setResolvingAlertId] = useState(null);\n  const [timelineAlert, setTimelineAlert] = useState(null);"
    content = content.replace(state_target, state_replacement)

    # Button
    action_target = """<div className="alert-feed-actions" style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>"""
    action_replacement = action_target + """
                <Button onClick={() => setTimelineAlert(alert)} variant="ghost" size="small">Timeline</Button>"""
    content = content.replace(action_target, action_replacement)

    # Modal rendering
    end_target = "{resolvingAlertId && <ResolveAlertModal onClose={() => setResolvingAlertId(null)} onSubmit={handleResolveSubmit} />}"
    end_replacement = end_target + "\n      {timelineAlert && <TimelineModal alert={timelineAlert} onClose={() => setTimelineAlert(null)} />}"
    content = content.replace(end_target, end_replacement)

    with open(path, "w") as f:
        f.write(content)

if __name__ == "__main__":
    patch_alerts_timeline()
    print("Timeline added to Alerts.jsx")
