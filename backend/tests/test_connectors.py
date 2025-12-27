import pytest
import os
from manus_pro_server.connectors.local_device import LocalDeviceConnector
from manus_pro_server.connectors.base import ConnectorCapability

@pytest.mark.asyncio
async def test_local_device_connector(tmp_path):
    # إعداد الموصل مع مسار مؤقت
    config = {"root_path": str(tmp_path)}
    connector = LocalDeviceConnector(connector_id="test_ld", name="Test LD", config=config)
    
    # اختبار الاتصال
    assert await connector.connect() is True
    
    # اختبار الإرسال (كتابة ملف)
    payload = {"path": "test.txt", "content": "hello world", "mode": "w"}
    result = await connector.send(payload)
    assert result["success"] is True
    assert os.path.exists(tmp_path / "test.txt")
    
    # اختبار الجلب (قراءة ملف)
    fetch_res = await connector.fetch({"path": "test.txt"})
    assert len(fetch_res) == 1
    assert fetch_res[0]["content"] == "hello world"
    
    # اختبار الرفع
    local_file = tmp_path / "local.txt"
    local_file.write_text("local content")
    assert await connector.upload(str(local_file), "remote.txt") is True
    assert os.path.exists(tmp_path / "remote.txt")

def test_connector_capabilities():
    config = {"root_path": "/tmp"}
    connector = LocalDeviceConnector(connector_id="test", name="Test", config=config)
    assert ConnectorCapability.READ in connector.capabilities
    assert ConnectorCapability.WRITE in connector.capabilities
