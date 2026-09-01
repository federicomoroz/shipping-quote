def _payload(**overrides):
    defaults = dict(
        weight_kg=4, length_cm=30, width_cm=20, height_cm=15, declared_value_ars=25000, postal_code=1425
    )
    defaults.update(overrides)
    return defaults


async def test_post_quote_returns_three_results_and_ordered_trace(client, monkeypatch):
    monkeypatch.setattr("app.external_mocks.carrier_mocks.random.random", lambda: 0.99)

    response = await client.post("/api/quote", json=_payload())
    assert response.status_code == 200
    data = response.json()

    assert data["zone"] == "AMBA"
    assert len(data["results"]) == 3
    assert all(r["ok"] for r in data["results"])

    steps_seen = [entry["step"] for entry in data["trace"]]
    assert steps_seen[0] == "entrada"
    assert steps_seen[1] == "adaptador_primario"
    assert steps_seen[2] == "puerto_primario"
    assert steps_seen[3] == "caso_de_uso"
    assert "salida" in steps_seen
    assert "adaptador_secundario" in steps_seen


async def test_post_quote_rejects_overweight_package(client):
    response = await client.post("/api/quote", json=_payload(weight_kg=45))
    assert response.status_code == 422


async def test_get_history_lists_previous_quotes(client, monkeypatch):
    monkeypatch.setattr("app.external_mocks.carrier_mocks.random.random", lambda: 0.99)

    await client.post("/api/quote", json=_payload(postal_code=8400))

    response = await client.get("/api/history")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) >= 1
    assert rows[0]["zone"] == "Patagonia"
