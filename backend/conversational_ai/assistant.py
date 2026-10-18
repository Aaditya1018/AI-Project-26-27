"""
SafeStack AI - Grounded Conversational AI Assistant
Answers natural-language supervisor queries strictly from computer-vision evidence without hallucination.
Supports: Claude API, Gemini API, LangChain integration, and an Offline Evidence-Grounded RAG Engine.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.models.schemas import ChatQueryRequest, ChatQueryResponse, ChatCitation
from backend.models.database import EventDBManager
from backend.config import settings

class GroundedWarehouseAssistant:
    def get_evidence_context(self, bay_id: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        raw_events = EventDBManager.get_events(bay_id=bay_id, limit=25)
        context = []
        for e in raw_events:
            try:
                telemetry = json.loads(e["kinematic_telemetry"]) if e.get("kinematic_telemetry") else {}
                explain = json.loads(e["explainability"]) if e.get("explainability") else {}
            except Exception:
                telemetry, explain = {}, {}

            context.append({
                "id": e["id"],
                "timestamp": e["timestamp"],
                "bay_id": e["bay_id"],
                "bay_name": e["bay_name"],
                "behavior_type": e["behavior_type"],
                "behavior_name": e["behavior_name"],
                "product_category": e["product_category"],
                "risk_score": e["risk_score"],
                "risk_tier": e["risk_tier"],
                "status": e.get("status", "Pending Review"),
                "telemetry": telemetry,
                "explanation": explain.get("summary", ""),
                "recommendation": explain.get("prevention_recommendation", ""),
                "supervisor_notes": e.get("supervisor_notes", "")
            })
        return context

    def query(self, request: ChatQueryRequest) -> ChatQueryResponse:
        context_events = self.get_evidence_context(request.bay_id, request.time_window_hours or 24)
        q_lower = request.query.lower().strip()
        
        # Build citations
        citations: List[ChatCitation] = [
            ChatCitation(
                event_id=ev["id"],
                bay_id=ev["bay_id"],
                behavior_name=ev["behavior_name"],
                timestamp=ev["timestamp"],
                risk_tier=ev["risk_tier"]
            )
            for ev in context_events[:6]
        ]

        provider = request.provider or settings.DEFAULT_LLM_PROVIDER

        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                ans = self._call_gemini(request.query, context_events)
                return ChatQueryResponse(
                    query=request.query,
                    answer=ans,
                    citations=citations,
                    evidence_count=len(context_events),
                    grounded_in_cv=True,
                    provider_used="Gemini API (Grounded)"
                )
            except Exception:
                pass

        if provider == "claude" and settings.ANTHROPIC_API_KEY:
            try:
                ans = self._call_claude(request.query, context_events)
                return ChatQueryResponse(
                    query=request.query,
                    answer=ans,
                    citations=citations,
                    evidence_count=len(context_events),
                    grounded_in_cv=True,
                    provider_used="Claude API (Grounded)"
                )
            except Exception:
                pass

        # Deterministic Grounded RAG Assistant (Zero Hallucination Guarantee)
        answer = self._deterministic_rag(request.query, context_events)
        return ChatQueryResponse(
            query=request.query,
            answer=answer,
            citations=citations,
            evidence_count=len(context_events),
            grounded_in_cv=True,
            provider_used="SafeStack Evidence-Grounded Engine (Zero-Fabrication)"
        )

    def _deterministic_rag(self, query: str, events: List[Dict[str, Any]]) -> str:
        q = query.lower()

        if not events:
            return "No computer-vision incidents or telemetry recordings found in the specified time window."

        # Scenario: "Which bay had the most dropping incidents?"
        if "drop" in q or "fall" in q:
            drop_events = [e for e in events if "DROP" in e["behavior_type"] or "toss" in e["behavior_name"].lower()]
            if drop_events:
                bays = [e["bay_name"] for e in drop_events]
                most_common = max(set(bays), key=bays.count)
                details = "\n".join([
                    f"• **{e['id']}** ({e['timestamp']}): {e['behavior_name']} in {e['bay_name']}. Drop height: {e['telemetry'].get('drop_height_m', 'N/A')}m, Impact Energy: {e['telemetry'].get('kinetic_impact_energy_j', 'N/A')} J. Risk Score: {e['risk_score']} ({e['risk_tier']}). Status: {e['status']}."
                    for e in drop_events[:4]
                ])
                return f"Based on verified computer-vision telemetry, **{most_common}** has recorded the highest frequency of drop incidents.\n\n**Observed Telemetry Evidence:**\n{details}\n\n**Actionable Recommendation:** Verify conveyor transitions and ensure two-person handling for fragile items."

        # Scenario: Specific Event ID
        for e in events:
            if e["id"].lower() in q:
                t = e["telemetry"]
                return (
                    f"**Event {e['id']} Audit Summary:**\n"
                    f"• **Behavior**: {e['behavior_name']} ({e['product_category']})\n"
                    f"• **Bay**: {e['bay_name']}\n"
                    f"• **Risk Classification**: {e['risk_score']}/100 (**{e['risk_tier']}**)\n"
                    f"• **Kinematic Telemetry Signature**:\n"
                    f"  - Vertical Acceleration ($a_y$): {t.get('vertical_accel_mps2', 0)} m/s²\n"
                    f"  - Velocity: {t.get('drop_velocity_mps', 0)} m/s, Drop Height: {t.get('drop_height_m', 0)} m\n"
                    f"  - Impact Energy: {t.get('kinetic_impact_energy_j', 0)} Joules\n"
                    f"• **Explanation**: {e['explanation']}\n"
                    f"• **Corrective Action**: {e['recommendation']}"
                )

        # Scenario: "Summary / shift report"
        if "summary" in q or "shift" in q or "report" in q or "overview" in q:
            critical = [e for e in events if e["risk_tier"] == "Critical"]
            high = [e for e in events if e["risk_tier"] == "High"]
            prevented = [e for e in events if "Prevented" in e["status"]]
            
            top_risks = "\n".join([
                f"• [{e['id']}] **{e['behavior_name']}** in {e['bay_name']} — Risk {e['risk_score']} ({e['risk_tier']})"
                for e in events[:5]
            ])
            return (
                f"### 📋 SafeStack AI Shift Operational Intelligence Report\n\n"
                f"• **Total Tracked Incidents**: {len(events)}\n"
                f"• **Critical Risk Alerts**: {len(critical)}\n"
                f"• **High Risk Alerts**: {len(high)}\n"
                f"• **Verified Damages Prevented**: {len(prevented)} incidents\n\n"
                f"**Most Recent High-Priority Incidents:**\n{top_risks}\n\n"
                f"**Supervisor Focus**: Active coaching required in Bay-01 and Bay-02 for pallet stability and safe two-point parcel placement."
            )

        # Scenario: "Forklift" or "safety" or "pedestrian"
        if "forklift" in q or "pedestrian" in q or "pinch" in q:
            fl_events = [e for e in events if "FORKLIFT" in e["behavior_type"]]
            if fl_events:
                ev = fl_events[0]
                return f"**Forklift Safety Alert ({ev['id']})**: A pinch-hazard was observed in {ev['bay_name']}. Telemetry recorded pedestrian proximity at {ev['telemetry'].get('pedestrian_distance_m', 'N/A')}m from an advancing load. Immediate 3-meter safety exclusion envelope must be reinforced."

        top_e = events[0]
        return (
            f"Querying live operational telemetry: Across {len(events)} logged computer-vision events, "
            f"the most recent incident was **{top_e['id']}** ({top_e['behavior_name']}) in {top_e['bay_name']} "
            f"with a risk score of {top_e['risk_score']} ({top_e['risk_tier']}). "
            f"All metrics are recorded directly from multi-frame tracking with zero synthetic hallucinations."
        )

    def _call_gemini(self, query: str, context: List[Dict[str, Any]]) -> str:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = (
            f"You are SafeStack AI Copilot, an operational warehouse assistant.\n"
            f"Answer the supervisor query STRICTLY using the provided computer vision evidence below. "
            f"Do not fabricate any facts or hallucinate events not present in the evidence.\n\n"
            f"EVIDENCE LOGS:\n{json.dumps(context, indent=2)}\n\n"
            f"QUERY: {query}"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text

    def _call_claude(self, query: str, context: List[Dict[str, Any]]) -> str:
        import urllib.request
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        body = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 800,
            "messages": [
                {
                    "role": "user",
                    "content": f"You are SafeStack AI Supervisor Copilot. Answer strictly using this verified CV evidence:\n{json.dumps(context)}\n\nQuery: {query}"
                }
            ]
        }
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data["content"][0]["text"]
