import os

def patch_equipment():
    path = r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\pages\Equipment.jsx"
    with open(path, "r") as f:
        content = f.read()

    # Import EquipmentTimeline
    import_target = "import LineChart from '../components/charts/LineChart';"
    import_replacement = "import LineChart from '../components/charts/LineChart';\nimport EquipmentTimeline from '../components/equipment/EquipmentTimeline';"
    content = content.replace(import_target, import_replacement)

    # In Modal Header: add Lifecycle info
    lifecycle_target = """<div style={{ marginTop: '8px', display: 'flex', gap: '8px' }}>
                  <Badge status={inspectDetail.status}>{inspectDetail.status}</Badge>
                  <span style={{ fontSize: '0.85rem', color: 'var(--color-on-dark-muted)' }}>
                    Installed: {new Date(inspectDetail.install_date).toLocaleDateString()}
                  </span>
                </div>"""
    lifecycle_replacement = """<div style={{ marginTop: '8px', display: 'flex', gap: '8px' }}>
                  <Badge status={inspectDetail.status}>{inspectDetail.status}</Badge>
                </div>
                <div style={{ marginTop: '12px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.85rem', color: 'var(--color-on-dark-muted)' }}>
                  <span><strong>Installed:</strong> {inspectDetail.install_date ? new Date(inspectDetail.install_date).toLocaleDateString() : 'N/A'}</span>
                  <span><strong>Purchased:</strong> {inspectDetail.purchase_date ? new Date(inspectDetail.purchase_date).toLocaleDateString() : 'N/A'}</span>
                  <span><strong>Warranty:</strong> {inspectDetail.warranty_expiry ? new Date(inspectDetail.warranty_expiry).toLocaleDateString() : 'N/A'}</span>
                  <span><strong>Lifetime:</strong> {inspectDetail.expected_lifetime_years} years</span>
                  <span><strong>Value:</strong> ${inspectDetail.replacement_cost}</span>
                  <span><strong>Next Cal:</strong> {inspectDetail.last_calibration_date ? new Date(inspectDetail.last_calibration_date).toLocaleDateString() : 'N/A'}</span>
                </div>"""
    content = content.replace(lifecycle_target, lifecycle_replacement)

    # Replace maintenance history with Timeline
    timeline_target = """{/* Maintenance History list */}
            <h4 style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '0.5px' }}>Maintenance Log history</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '150px', overflowY: 'auto' }}>
              {maintenanceHistory.length > 0 ? (
                maintenanceHistory.map((log) => (
                  <div key={log.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', backgroundColor: 'var(--color-ink-deep)', border: '1px solid var(--color-hairline-violet)', borderRadius: 'var(--rounded-md)', fontSize: '0.85rem' }}>
                    <div>
                      <strong style={{ textTransform: 'capitalize' }}>{log.maintenance_type}</strong>
                      <div style={{ color: 'var(--color-on-dark-muted)' }}>{log.description}</div>
                    </div>
                    <div style={{ textDirection: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                      <span style={{ color: 'var(--color-accent-lime)' }}>${log.cost}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-faint)' }}>{new Date(log.performed_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '12px', color: 'var(--color-on-dark-muted)', fontSize: '0.85rem' }}>
                  No maintenance records registered for this machine.
                </div>
              )}
            </div>"""
    timeline_replacement = """{/* Asset History Timeline */}
            <h4 style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '0.5px', marginTop: '16px' }}>Asset Timeline</h4>
            <div style={{ maxHeight: '300px', overflowY: 'auto', border: '1px solid var(--color-hairline-violet)', borderRadius: 'var(--rounded-md)', backgroundColor: 'var(--color-surface-night)' }}>
              <EquipmentTimeline equipmentId={inspectDetail.id} />
            </div>"""
    content = content.replace(timeline_target, timeline_replacement)

    with open(path, "w") as f:
        f.write(content)

if __name__ == "__main__":
    patch_equipment()
    print("Equipment frontend updated.")
