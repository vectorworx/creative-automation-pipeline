"""
Workflow Integrator
Simulates stakeholder notifications and approval chains.
"""
def notify(role, message):
    print(f"[{role}] {message}")

def approval_sim(product_id):
    notify("Creative Director", f"Approved visuals for {product_id}")
    return True
