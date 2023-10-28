from qiskit import *
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from qiskit_ionq import IonQProvider
from decouple import config
from azure.quantum.qiskit import AzureQuantumProvider

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

def get_provider(backend_name):
    if backend_name == "ionq_simulator":
        api_key = config("IONQ_API_KEY")
        provider = IonQProvider(api_key)
    elif backend_name == "quantinuum.sim.h1-2sc":
        resource_id = config("AZURE_RESOURCE_ID")
        location = config("AZURE_LOCATION")
        provider = AzureQuantumProvider(resource_id=resource_id,location=location)
    else:
        api_key = config("IBM_API_KEY")
        IBMQ.save_account(api_key)
        provider = IBMQ.load_account()
    return provider

class Circuit(BaseModel):
    qasm: str

@app.post("/circuit")
async def create_circuit(circuit: Circuit, backend_name: str | None = "ibmq_qasm_simulator"):
    try:
      circuit = QuantumCircuit.from_qasm_str(circuit.qasm)
      provider = get_provider(backend_name)
      backend = provider.get_backend(backend_name)
      transpiled = transpile(circuit, backend=backend)
      job = backend.run(transpiled)
      return {"jobId": job.job_id()}
    except:
      raise HTTPException(400, "Invalid Circuit")

@app.post("/draw")
async def draw_circuit(circuit: Circuit):
    try:
      circuit = QuantumCircuit.from_qasm_str(circuit.qasm)
      drawn_image = circuit.draw(output="mpl")
      buffer = BytesIO()
      drawn_image.savefig(buffer, format="png")
      buffer.seek(0)

      return StreamingResponse(buffer, media_type="image/png")
    except:
      raise HTTPException(400, "Invalid Circuit")

@app.post("/result/{job_id}")
def get_result(job_id: str, backend_name: str | None = "ibmq_qasm_simulator"):
    provider = get_provider(backend_name)
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