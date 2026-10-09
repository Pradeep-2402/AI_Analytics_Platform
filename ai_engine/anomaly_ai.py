from ai_engine.ollama_client import ask_ollama

def explain_anomalies(anomalies):

    if len(anomalies) == 0:

        return "No significant anomalies detected."

    prompt = f"""
Detected Anomalies:

{anomalies}

Generate:

1. Severity
2. Business Impact
3. Root Cause
4. Recommendation
5. Risk Level

Keep answer under 100 words.
"""

    return ask_ollama(prompt)