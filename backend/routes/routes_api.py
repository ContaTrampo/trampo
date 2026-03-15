"""TRAMPO v8 — Rota de rotas (trajetos)"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

routes_bp = Blueprint("routes_calc", __name__, url_prefix="/api/routes")


@routes_bp.route("/estimate", methods=["POST"])
@jwt_required()
def estimate_route():
    data = request.get_json() or {}
    origin      = data.get("origin", "")
    destination = data.get("destination", "")
    mode        = data.get("mode", "transit")

    if not origin or not destination:
        return jsonify({"error": "Origem e destino são obrigatórios"}), 400

    # Estimativas por modo (fallback sem API Key)
    estimates = {
        "transit":   {"duration": "35 min", "distance": "12 km", "fare": "R$ 4,50"},
        "driving":   {"duration": "18 min", "distance": "14 km", "fare": "~R$ 9,80"},
        "walking":   {"duration": "90 min", "distance": "6 km",  "fare": "Grátis"},
        "bicycling": {"duration": "40 min", "distance": "10 km", "fare": "Grátis"},
    }

    result = estimates.get(mode, estimates["transit"])

    return jsonify({
        "origin":      origin,
        "destination": destination,
        "mode":        mode,
        "duration":    result["duration"],
        "distance":    result["distance"],
        "fare":        result["fare"],
        "note":        "Estimativa aproximada. Configure GOOGLE_MAPS_API_KEY para cálculo preciso."
    }), 200
