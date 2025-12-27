import { useEffect, useState } from "react";
import { getSettings, setApiKeys } from "../api";

export function SettingsPanel(props: { onChanged?: ()=>void }){
  const [status, setStatus] = useState<any>(null);
  const [keys, setKeys] = useState({
    api_key_1: "",
    api_key_2: "",
    api_key_3: "",
    api_key_4: "",
    api_key_5: "",
  });
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function refresh(){
    setErr(null);
    try{
      setStatus(await getSettings());
    }catch(e:any){
      setErr(String(e?.message || e));
    }
  }

  useEffect(()=>{ refresh(); }, []);

  async function save(){
    setSaving(true);
    setErr(null);
    setSuccess(null);
    try{
      const response = await setApiKeys(keys);
      
      if (!response || !response.updated_slots || response.updated_slots.length === 0) {
        throw new Error("لم يتم حفظ أي مفتاح — الرجاء التحقق من الخادم.");
      }
      
      setKeys({
        api_key_1: "",
        api_key_2: "",
        api_key_3: "",
        api_key_4: "",
        api_key_5: "",
      });
      
      await refresh();
      setSuccess("✅ تم حفظ المفاتيح بنجاح!");
      props.onChanged?.();
      setTimeout(() => setSuccess(null), 3000);
    }catch(e:any){
      setErr(String(e?.message || e));
    }finally{
      setSaving(false);
    }
  }

  const hasAnyKey = Object.values(keys).some(k => k.trim().length >= 10);
  const configuredCount = Object.values(status?.api_keys_configured || {}).filter(Boolean).length;

  return (
    <div className="panel">
      <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20}}>
        <div style={{fontSize: 32}}>🛠️</div>
        <div>
          <div style={{fontWeight:900, fontSize: 22}}>الإعدادات</div>
          <div className="small">إدارة مفاتيح API والإعدادات العامة</div>
        </div>
      </div>

      <div style={{padding: 16, background: 'linear-gradient(135deg, rgba(34,197,94,0.15), rgba(16,185,129,0.1))', borderRadius: 12, border: '1px solid rgba(34,197,94,0.3)', marginBottom: 20}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
          <div style={{fontSize: 32}}>🔑</div>
          <div>
            <div style={{fontWeight: 700, fontSize: 16, marginBottom: 4}}>المفاتيح المضبوطة: {configuredCount}/5</div>
            <div className="small">يتم توزيع المهام تلقائياً على جميع المفاتيح المتاحة</div>
          </div>
        </div>
      </div>

      <div style={{marginTop:20}}>
        <div style={{fontWeight: 700, fontSize: 18, marginBottom: 16}}>🔐 مفاتيح Cerebras API</div>
        <div className="small" style={{marginBottom: 16, padding: 12, background: 'rgba(59,130,246,0.1)', borderRadius: 8, border: '1px solid rgba(59,130,246,0.3)'}}>
          💡 يمكنك إضافة حتى 5 مفاتيح API مختلفة. المفاتيح مشفرة ومحفوظة بشكل آمن على السيرفر فقط.
        </div>
        
        <div style={{display: 'grid', gap: 16}}>
          {[1, 2, 3, 4, 5].map(num => {
            const keyName = `api_key_${num}` as keyof typeof keys;
            const isConfigured = status?.api_keys_configured?.[keyName] || false;
            
            return (
              <div 
                key={num} 
                style={{
                  padding: 16, 
                  background: isConfigured ? 'rgba(34,197,94,0.08)' : 'rgba(148,163,184,0.05)', 
                  borderRadius: 12, 
                  border: `1px solid ${isConfigured ? 'rgba(34,197,94,0.3)' : 'var(--border)'}`
                }}
              >
                <div className="row" style={{marginBottom: 10}}>
                  <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                    <div style={{fontSize: 20}}>{isConfigured ? '✅' : '⚪'}</div>
                    <div style={{fontWeight: 700, fontSize: 15}}>API Key {num}</div>
                  </div>
                  <div className={"badge " + (isConfigured ? "good" : "warn")}>
                    {isConfigured ? "مضبوط ✓" : "غير مضبوط"}
                  </div>
                </div>
                <input 
                  className="input" 
                  value={keys[keyName]} 
                  onChange={(e)=>setKeys({...keys, [keyName]: e.target.value})} 
                  placeholder={`أدخل API Key ${num} هنا... (sk-...)`}
                  type="password"
                  style={{fontSize: 13}}
                />
              </div>
            );
          })}
        </div>

        <div className="row" style={{marginTop: 20}}>
          <button 
            className="btn" 
            onClick={save} 
            disabled={saving || !hasAnyKey}
            style={{flex: 1, fontSize: 15, padding: '14px 24px'}}
          >
            💾 حفظ جميع المفاتيح
          </button>
          <button 
            className="btn secondary" 
            onClick={refresh} 
            disabled={saving}
            style={{padding: '14px 24px'}}
          >
            🔄 تحديث
          </button>
        </div>
        
        {err && (
          <div style={{marginTop: 12, padding: 12, background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, color: '#ef4444', fontSize: 13, fontWeight: 600}}>
            ⚠️ {err}
          </div>
        )}
        
        {success && (
          <div style={{marginTop: 12, padding: 12, background: 'rgba(34,197,94,0.15)', border: '1px solid rgba(34,197,94,0.3)', borderRadius: 8, color: '#22c55e', fontSize: 13, fontWeight: 600}}>
            {success}
          </div>
        )}
      </div>

      <div style={{marginTop: 30, padding: 16, background: 'rgba(11,18,32,0.6)', borderRadius: 12, border: '1px solid var(--border)'}}>
        <div style={{fontWeight: 700, fontSize: 16, marginBottom: 12}}>📊 معلومات النظام</div>
        
        <div style={{marginBottom: 16}}>
          <div className="small" style={{marginBottom: 8, fontWeight: 600}}>النماذج المتاحة:</div>
          <div className="mono" style={{padding: 12}}>
            {status?.models && status.models.length > 0 ? (
              status.models.map((m: any, i: number) => (
                <div key={i} style={{marginBottom: 4}}>
                  • {m.id} (Context: {m.context}, Tier: {m.tier}, Stage: {m.stage})
                </div>
              ))
            ) : (
              <div style={{color: 'var(--muted)'}}>لا توجد نماذج متاحة حالياً</div>
            )}
          </div>
        </div>

        <div>
          <div className="small" style={{marginBottom: 8, fontWeight: 600}}>الحصص المتاحة (Quotas):</div>
          <div className="mono" style={{padding: 12}}>
            {status?.quotas && Object.keys(status.quotas).length > 0 ? (
              Object.entries(status.quotas).map(([key, value]) => (
                <div key={key} style={{marginBottom: 4}}>
                  • {key}: {String(value)}
                </div>
              ))
            ) : (
              <div style={{color: 'var(--muted)'}}>لا توجد معلومات حصص متاحة</div>
            )}
          </div>
        </div>
      </div>

      <div style={{marginTop: 20, padding: 16, background: 'linear-gradient(135deg, rgba(124,58,237,0.15), rgba(147,51,234,0.1))', borderRadius: 12, border: '1px solid rgba(124,58,237,0.3)'}}>
        <div style={{display: 'flex', alignItems: 'flex-start', gap: 12}}>
          <div style={{fontSize: 24}}>💡</div>
          <div>
            <div style={{fontWeight: 700, fontSize: 14, marginBottom: 6, color: 'var(--accent)'}}>نصيحة مهمة:</div>
            <div className="small" style={{lineHeight: 1.6}}>
              سيتم توزيع المهام تلقائياً على جميع المفاتيح المتاحة لزيادة السرعة وتحسين استخدام الحصص. 
              كلما زاد عدد المفاتيح المضبوطة، زادت قدرة النظام على معالجة المهام المتعددة بشكل متوازي.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
