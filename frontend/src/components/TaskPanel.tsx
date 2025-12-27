import { useEffect, useState } from "react";
import { cancelTask, createTask, listTasks, type TaskSummary } from "../api";

function fmtSec(sec: number): string{
  if(!isFinite(sec) || sec < 0) return "--";
  const s = Math.round(sec);
  const h = Math.floor(s/3600);
  const m = Math.floor((s%3600)/60);
  const r = s%60;
  const hh = h>0 ? `${h}س ` : "";
  return `${hh}${m}د ${r}ث`;
}

function badgeClass(status: string): string{
  if(status === "completed") return "good";
  if(status === "running") return "warn";
  if(status === "waiting") return "warn";
  if(status === "error" || status === "cancelled") return "bad";
  return "";
}

export function TaskPanel(props: { onSelect:(t:TaskSummary)=>void; selectedId?:string }){
  const [tasks, setTasks] = useState<TaskSummary[]>([]);
  const [goal, setGoal] = useState("");
  const [projectPath, setProjectPath] = useState(".");
  const [budget, setBudget] = useState(1000000);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function refresh(){
    try{
      const r = await listTasks();
      setTasks(Array.isArray(r) ? r : []);
    }catch(e:any){
      console.error(e);
    }
  }

  useEffect(()=>{
    refresh();
    const t = setInterval(refresh, 2000);
    return ()=> clearInterval(t);
  }, []);

  async function startTask(){
    setLoading(true);
    setErr(null);
    try{
      const r = await createTask(goal, projectPath, budget);
      setGoal("");
      await refresh();
      if(r.ok && r.task_id) {
        const allTasks = await listTasks();
        const newTask = allTasks.find((t: any) => t.id === r.task_id);
        if(newTask) props.onSelect(newTask);
      }
    }catch(e:any){
      setErr(String(e?.message || e));
    }finally{
      setLoading(false);
    }
  }

  async function cancel(id: string){
    setLoading(true);
    setErr(null);
    try{
      await cancelTask(id);
      await refresh();
    }catch(e:any){
      setErr(String(e?.message || e));
    }finally{
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20}}>
        <div style={{fontSize: 32}}>⚙️</div>
        <div>
          <div style={{fontWeight:900, fontSize: 22}}>إدارة المهام</div>
          <div className="small">إنشاء ومتابعة المهام المعقدة</div>
        </div>
      </div>

      <div style={{marginTop:20, padding: 20, background: 'linear-gradient(135deg, rgba(124,58,237,0.15), rgba(147,51,234,0.1))', borderRadius: 14, border: '1px solid rgba(124,58,237,0.3)'}}>
        <div style={{fontWeight: 700, marginBottom: 12, fontSize: 16}}>✨ إنشاء مهمة جديدة</div>
        
        <div className="small" style={{marginBottom: 8, fontWeight: 600}}>وصف المهمة</div>
        <textarea 
          value={goal} 
          onChange={(e)=>setGoal(e.target.value)} 
          placeholder="مثال: حلل المشروع وحدد الثغرات، نفّذ إصلاحات شاملة، اكتب تقريراً تفصيلياً كاملاً..."
          style={{minHeight: 100}}
        />
        
        <div style={{display: 'grid', gridTemplateColumns: '1fr 200px', gap: 12, marginTop: 12}}>
          <div>
            <div className="small" style={{marginBottom: 6, fontWeight: 600}}>مسار المشروع داخل Workspace</div>
            <input className="input" value={projectPath} onChange={(e)=>setProjectPath(e.target.value)} />
          </div>
          <div>
            <div className="small" style={{marginBottom: 6, fontWeight: 600}}>ميزانية التوكنات</div>
            <input className="input" type="number" value={budget} onChange={(e)=>setBudget(Number(e.target.value))} />
          </div>
        </div>
        
        <div className="row" style={{marginTop: 16}}>
          <button 
            className="btn" 
            onClick={startTask} 
            disabled={loading || goal.trim().length<3}
            style={{flex: 1, fontSize: 15, padding: '14px 24px'}}
          >
            🚀 ابدأ المهمة الآن
          </button>
          <button 
            className="btn secondary" 
            onClick={refresh} 
            disabled={loading}
            style={{padding: '14px 24px'}}
          >
          </button>
        </div>
        
        {err && (
          <div style={{marginTop: 12, padding: 12, background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, color: '#ef4444', fontSize: 13, fontWeight: 600}}>
            ⚠️ {err}
          </div>
        )}
      </div>

      <div style={{marginTop: 24}}>
        <div style={{fontWeight: 700, fontSize: 18, marginBottom: 12}}>📋 قائمة المهام ({tasks.length})</div>
        
        {tasks.length === 0 && (
          <div style={{textAlign: 'center', padding: 60, color: 'var(--muted)'}}>
            <div style={{fontSize: 64, marginBottom: 16, opacity: 0.5}}>📭</div>
            <div style={{fontSize: 18, fontWeight: 700, marginBottom: 8}}>لا توجد مهام حالياً</div>
            <div style={{fontSize: 14}}>قم بإنشاء مهمة جديدة للبدء</div>
          </div>
        )}

        <div className="list">
          {tasks.map(t => (
            <div 
              key={t.id} 
              className="item" 
              style={{
                borderColor: props.selectedId===t.id ? "rgba(124,58,237,0.8)" : undefined,
                borderWidth: props.selectedId===t.id ? 2 : 1,
                boxShadow: props.selectedId===t.id ? '0 0 20px rgba(124,58,237,0.3)' : undefined
              }}
              onClick={()=>props.onSelect(t)}
            >
              <div className="row" style={{marginBottom: 10}}>
                <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                  <div className="mono" style={{fontWeight:900, fontSize: 14, color: 'var(--accent)'}}>#{t.id}</div>
                  <div className={"badge " + badgeClass(t.status)}>{t.status}</div>
                </div>
                <div className="small">{new Date().toLocaleString('ar-SA')}</div>
              </div>
              
              <div style={{fontSize: 15, fontWeight: 600, lineHeight: 1.5, marginBottom: 12}}>
                {t.goal.slice(0,200)}{t.goal.length>200?"...":""}
              </div>

              <div style={{marginTop:12}}>
                <div className="progress">
                  <div style={{width: `${Math.round((t.progress||0)*100)}%`}} />
                </div>
                
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 10}}>
                  <div style={{padding: 8, background: 'rgba(124,58,237,0.1)', borderRadius: 8}}>
                    <div className="small" style={{marginBottom: 4}}>⏱️ الوقت المنقضي</div>
                    <div style={{fontWeight: 700, fontSize: 14}}>{fmtSec(t.elapsed_seconds||0)}</div>
                  </div>
                  <div style={{padding: 8, background: 'rgba(34,197,94,0.1)', borderRadius: 8}}>
                    <div className="small" style={{marginBottom: 4}}>⏳ الوقت المتبقي</div>
                    <div style={{fontWeight: 700, fontSize: 14}}>{fmtSec(t.eta_seconds||0)}</div>
                  </div>
                  <div style={{padding: 8, background: 'rgba(245,158,11,0.1)', borderRadius: 8}}>
                    <div className="small" style={{marginBottom: 4}}>🎯 التوكنات</div>
                    <div style={{fontWeight: 700, fontSize: 14}}>{t.token_total}/{t.token_budget}</div>
                  </div>
                  <div style={{padding: 8, background: 'rgba(59,130,246,0.1)', borderRadius: 8}}>
                    <div className="small" style={{marginBottom: 4}}>📊 الخطوات</div>
                    <div style={{fontWeight: 700, fontSize: 14}}>{t.steps_done}/{t.steps_estimate}</div>
                  </div>
                </div>
                
                {t.last_error && (
                  <div style={{marginTop: 10, padding: 10, background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.3)', borderRadius: 8, fontSize: 13}}>
                    <div style={{fontWeight: 700, color: '#f59e0b', marginBottom: 4}}>⚠️ آخر ملاحظة:</div>
                    <div style={{color: '#fbbf24'}}>{t.last_error}</div>
                  </div>
                )}
              </div>

              <div className="row" style={{marginTop:16}}>
                <button 
                  className="btn" 
                  onClick={(e)=>{e.stopPropagation(); props.onSelect(t);}}
                  style={{flex: 1, background: 'linear-gradient(135deg, #10b981, #059669)'}}
                >
                  📊 عرض الأحداث
                </button>
                <button 
                  className="btn danger" 
                  onClick={(e)=>{e.stopPropagation(); cancel(t.id);}} 
                  disabled={loading || (t.status==="completed"||t.status==="cancelled")}
                >
                  ❌ إلغاء
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
