import numpy as np
from qiskit import *

IBMQ.save_account('7349a272aefcd3e7c27cfea35a5275b8482cacd5e4080610a998b4f42af1affdf5fc027eeac38e566aa275547dfca2508429ce867871d4e0dfc93d937eee328f', overwrite=True)
provider = IBMQ.load_account()

circ = QuantumCircuit(3)
circ.h(2)
circ.x(0)
circ.cx(0, 1)
circ.cx(0, 2)

circ.measure_all()

print(circ.qasm())

#circ.draw(output='mpl')


# backends = provider.backends()
# print(backends)

# #backend_name = "ibmq_qasm_simulator"
# backend_name = "ibm_lagos"

# backend = provider.get_backend(backend_name)
# transpiled = transpile(circ, backend=backend)
# job = backend.run(transpiled)
# job_id = job.job_id()
# print(job_id)

# job = provider.get_backend(backend_name).retrieve_job(job_id)
# result = job.result()
# print(result)

# counts = result.get_counts(circ)
# print(counts)
