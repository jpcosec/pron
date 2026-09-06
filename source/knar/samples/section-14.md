# 14. API como nodo

```yaml
id: weather_api

runtime:
  type: http

inputs:
  - WeatherRequest

outputs:
  - WeatherObservation

capabilities:
  - current_weather

auth:
  strategy: secret_ref
  secret: WEATHER_API_KEY
```

El detalle HTTP queda encapsulado.

---

