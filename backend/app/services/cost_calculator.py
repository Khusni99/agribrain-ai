from app.schemas.diagnosis import CostCalculationRequest, CostCalculationResponse


class CostCalculator:
    def __init__(self):
        self.default_items = {
            "seeds": {"label": "Benih", "default_qty": 1, "unit": "kg"},
            "fertilizer_npk": {"label": "Pupuk NPK", "default_qty": 400, "unit": "kg"},
            "fertilizer_urea": {"label": "Pupuk Urea", "default_qty": 200, "unit": "kg"},
            "pesticide": {"label": "Pestisida", "default_qty": 10, "unit": "liter"},
            "labor_planting": {"label": "Tenaga Kerja Tanam", "default_qty": 20, "unit": "HOK"},
            "labor_maintenance": {"label": "Tenaga Kerja Pemeliharaan", "default_qty": 30, "unit": "HOK"},
            "irrigation": {"label": "Irigasi", "default_qty": 1, "unit": "musim"},
            "fuel": {"label": "Bahan Bakar", "default_qty": 50, "unit": "liter"},
            "packaging": {"label": "Kemasan", "default_qty": 500, "unit": "buah"},
            "transportation": {"label": "Transportasi", "default_qty": 1, "unit": "kali"},
        }

    async def calculate(self, data: CostCalculationRequest) -> CostCalculationResponse:
        total_cost = sum(item.get("total_cost", item.get("quantity", 0) * item.get("unit_price", 0))
                        for item in data.items)

        estimated_yield_kg = data.area_hectare * 15000
        cost_per_plant = total_cost / (data.area_hectare * 10000)
        cost_per_hectare = total_cost / data.area_hectare
        cost_per_kg = total_cost / estimated_yield_kg if estimated_yield_kg > 0 else 0

        estimated_revenue = estimated_yield_kg * 5000
        profit = estimated_revenue - total_cost
        roi = (profit / total_cost) * 100 if total_cost > 0 else 0

        breakdown = [
            {
                "category": item.get("name", f"Item {i+1}"),
                "quantity": item.get("quantity", 0),
                "unit": item.get("unit", ""),
                "unit_price": item.get("unit_price", 0),
                "total": item.get("total_cost", item.get("quantity", 0) * item.get("unit_price", 0)),
                "percentage": round(
                    (item.get("total_cost", 0) / total_cost * 100) if total_cost > 0 else 0, 1
                ),
            }
            for i, item in enumerate(data.items)
        ]

        return CostCalculationResponse(
            cost_per_plant=round(cost_per_plant, 2),
            cost_per_hectare=round(cost_per_hectare, 0),
            cost_per_kg=round(cost_per_kg, 2),
            total_cost=round(total_cost, 0),
            estimated_revenue=round(estimated_revenue, 0),
            profit_estimation=round(profit, 0),
            roi_percentage=round(roi, 1),
            breakdown=breakdown,
        )
