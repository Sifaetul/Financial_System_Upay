import re

with open("app/services/copilot_service.py", "r") as f:
    content = f.read()

if "MonitoringService.log_metric" not in content:
    # Add imports
    content = content.replace(
        "from .copilot_retrieval import HybridRetrieval",
        "from .copilot_retrieval import HybridRetrieval\nfrom .monitoring_service import MonitoringService\nimport time"
    )
    
    # Add timing and telemetry
    orig = "response_data = llm.generate_structured_response(question, context)"
    new = """
        start_t = time.time()
        response_data = llm.generate_structured_response(question, context)
        latency_ms = (time.time() - start_t) * 1000
        
        MonitoringService.log_metric(db, "copilot_latency_ms", "HISTOGRAM", latency_ms, "ai_investigation_copilot")
        MonitoringService.log_metric(db, "copilot_requests_total", "COUNTER", 1.0, "ai_investigation_copilot")
        
        if "LLM Error" in response_data.get("answer", "") or "Model inference failed" in response_data.get("uncertainties", []):
            MonitoringService.log_metric(db, "copilot_failures_total", "COUNTER", 1.0, "ai_investigation_copilot")
        
        MonitoringService.record_model_lineage(
            db=db,
            model_id="SmolLM2-135M",
            model_version="1.0",
            prediction=response_data.get("answer")[:50],
            correlation_id=conversation.id,
            confidence=0.5
        )
"""
    content = content.replace(orig, new)

with open("app/services/copilot_service.py", "w") as f:
    f.write(content)

