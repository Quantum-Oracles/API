from qiskit import *
from fastapi import FastAPI 
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("IBM_API_KEY")
IBMQ.save_account(api_key)
provider = IBMQ.load_account()

class Circuit(BaseModel):
    qasm: str

@app.post("/circuit")
async def create_circuit(circuit: Circuit, backend_name: str | None = "ibmq_qasm_simulator"):
    circuit = QuantumCircuit.from_qasm_str(circuit.qasm)
    backend = provider.get_backend(backend_name)
    transpiled = transpile(circuit, backend=backend)
    job = backend.run(transpiled)
    return job.job_id()

@app.post("/draw")
async def create_circuit(circuit: Circuit):
    circuit = QuantumCircuit.from_qasm_str(circuit.qasm)
    drawn_image = circuit.draw(output="mpl")
    buffer = BytesIO()
    drawn_image.savefig(buffer, format="png")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")

@app.post("/result/{job_id}")
def get_result(job_id: str, backend_name: str | None = "ibmq_qasm_simulator"):
    job = provider.get_backend(backend_name).retrieve_job(job_id)
    result = job.result()
    data = {}
    counts = result.results[0].data.counts
    max_s = 0
    for k in counts.keys():
        max_s = max(max_s, len(bin(int(k, 16))[2:]))
    
    for k in counts.keys():
        data[(bin(int(k, 16))[2:]).ljust(max_s, "0")] = counts[k]
    return data