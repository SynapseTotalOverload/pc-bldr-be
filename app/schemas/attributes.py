from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseAttrsSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    brand: str = Field(..., alias="Brand:")
    model: str = Field(..., alias="Model:")


class CPUAttributesSchema(BaseAttrsSchema):
    cores: int = Field(..., alias="Cores:")
    threads: int = Field(..., alias="Threads:")
    socket_type: str = Field(..., alias="Socket Type:")
    base_speed: float = Field(..., alias="Base Speed:")
    turbo_speed: float = Field(..., alias="Turbo Speed:")
    architechture: str = Field(..., alias="Architechture:")
    core_family: str = Field(..., alias="Core Family:")
    integrated_graphics: Optional[str] = Field(..., alias="Integrated Graphics:")
    memory_type: str = Field(..., alias="Memory Type:")
    memory_speed: int = Field(..., alias="Memory Speed:")
    series: str = Field(..., alias="Series:")
    generation: str = Field(..., alias="Generation:")


class CPUCoolerAttributesSchema(BaseAttrsSchema):
    fan_rpm_base: Optional[int] = Field(..., alias="Fan RPM:")
    fan_rpm_max: Optional[int] = Field(..., alias="Fan RPM Max:")
    noise_level_base: Optional[float] = Field(..., alias="Noise Level:")
    noise_level_max: Optional[float] = Field(..., alias="Noise Level Max:")
    color: str = Field(..., alias="Color:")


class MotherboardAttributesSchema(BaseAttrsSchema):
    chipset: str = Field(..., alias="Chipset:")
    form_factor: str = Field(..., alias="Form Factor:")
    socket_type: str = Field(..., alias="Socket Type:")
    ram_slots: int = Field(..., alias="Memory Slots:")
    max_ram_support: int = Field(..., alias="Max Memory Support:")


class RAMAttributesSchema(BaseAttrsSchema):
    total_memory: int = Field(..., alias="RAM Size:")
    one_unit_memory: int = Field(..., alias="Unit Ram Size:")
    quantity: int = Field(..., alias="Quantity:")
    ram_type: str = Field(..., alias="RAM Type:")
    ram_speed: int = Field(..., alias="RAM Speed:")
    cas_latency: str = Field(..., alias="CAS Latency:")


class StorageAttributesSchema(BaseAttrsSchema):
    capacity: Optional[int] = Field(..., alias="Capacity:")
    mem_type: str = Field(..., alias="Type:")
    interface: str = Field(..., alias="Interface:")
    cache_mem: Optional[int] = Field(..., alias="Cache Memory:")
    form_factor: str = Field(..., alias="Form Factor:")


class GPUAttributesSchema(BaseAttrsSchema):
    memory: float = Field(..., alias="Memory:")
    mem_interface: str = Field(..., alias="Memory Interface:")
    length: Optional[int] = Field(..., alias="Length:")
    interface: str = Field(..., alias="Interface:")
    chipset: str = Field(..., alias="Chipset:")
    base_clock: Optional[int] = Field(..., alias="Base Clock:")
    clock_speed: Optional[int] = Field(..., alias="Clock Speed:")
    frame_sync: str = Field(..., alias="Frame Sync:")


class PowerSupplyAttributesSchema(BaseAttrsSchema):
    power: Optional[int] = Field(..., alias="Power:")
    efficiency: str = Field(..., alias="Efficiency:")
    color: str = Field(..., alias="Color:")


class CaseAttributesSchema(BaseAttrsSchema):
    side_panel: str = Field(..., alias="Side Panel:")
    cabinet_type: str = Field(..., alias="Cabinet Type:")
    color: str = Field(..., alias="Color:")
