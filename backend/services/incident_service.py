from models.incident import IncidentCreate, IncidentResponse, IncidentUpdate
from services.base import CRUDService


class IncidentService(CRUDService[IncidentCreate, IncidentUpdate, IncidentResponse]):
    collection_name = "incidents"
    response_model = IncidentResponse
