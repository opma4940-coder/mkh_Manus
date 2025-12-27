import { useEffect, useRef, useState } from "react";
import { getEvents, type TaskEvent } from "../api";

function getLevelColor(level: string): string {
  if(level === "info") return "#3b82f6";
  if(level === "warning") return "#f59e0b";
  if(level === "error") return "#ef4444";
  if(level === "success") return "#22c55e";
  return "#94a3b8";
}

function getLevelIcon(level: string): string {
  if(level === "info") return "ℹ️";
  if(level === "warning") return "⚠️";
  if(level === "error") return "❌";
  if(level === "success") return "✅";
  return "📝";
}

export function EventsPanel(props: { taskId?: string }){
  const [events, setEvents] = useState<TaskEvent[]>([]);
  const [after, setAfter] = useState(0);
  const [err, setErr] = useState<string | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const boxRef = useRef<HTMLDivElement|null>(null);

  useEffect(()=>{
    setEvents([]);
    setAfter(0);
  }, [props.taskId]);

  useEffect(()=>{
    if(!props.taskId) return;

    let alive = true;
    const tick = async ()=>{
      try{
        const r = await getEvents(props.taskId!, after);
        if(!alive) return;
        const newEvents = Array.isArray(r.events) ? r.events : [];
        if(newEvents.length){
          setEvents(prev => [...prev, ...newEvents]);
          setAfter(newEvents[newEvents.length-1].id);
          if(autoScroll){
            setTimeout(()=>{ 
              boxRef.current?.scrollTo({top: boxRef.current.scrollHeight, behavior:"smooth"}); 
            }, 50);
          }
        }
        setErr(null);
      }catch(e:any){
        if(!alive) return;
        setErr(String(e?.message || e));
      }
    };

    const t = setInterval(tick, 1500);
    tick();

    return ()=>{
      alive = false;
      clearInterval(t);
    };
  }, [props.taskId, after, autoScroll]);

  return (
    <div className="panel" style={{minHeight: 500}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20}}>
        <div style={{fontSize: 32}}>📊</div>
        <div style={{flex: 1}}>
          <div style={{fontWeight:900, fontSize: 22}}>الأحداث والسجلات</div>
          <div className="small mono" style={{marginTop: 4}}>
            {props.taskId ? `Task ID: ${props.taskId}` : "لم يتم اختيار مهمة"}
          </div>
        </div>
        <div style={{display: 'flex', gap: 8}}>
          <button 
            className={`btn ${autoScroll ? '' : 'secondary'}`}
            onClick={() => setAutoScroll(!autoScroll)}
            style={{padding: '10px 16px', fontSize: 13}}
          >
            {autoScroll ? '🔄 التمرير التلقائي' : '⏸️ إيقاف التمرير'}
          </button>
          <button 
            className="btn secondary"
            onClick={() => {
              setEvents([]);
              setAfter(0);
            }}
            style={{padding: '10px 16px', fontSize: 13}}
          >
            🗑️ مسح
          </button>
        </div>
      </div>

      {err && (
        <div style={{marginBottom: 12, padding: 12, background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, color: '#ef4444', fontSize: 13, fontWeight: 600}}>
          ⚠️ {err}
        </div>
      )}

      <div 
        ref={boxRef} 
        style={{
          marginTop:12, 
          maxHeight: 600, 
          overflow:"auto", 
          border:"1px solid rgba(148,163,184,0.18)", 
          borderRadius:12, 
          padding:16,
          background: 'rgba(11,18,32,0.4)'
        }}
      >
        {events.length === 0 && (
          <div style={{textAlign: 'center', padding: 60, color: 'var(--muted)'}}>
            <div style={{fontSize: 64, marginBottom: 16, opacity: 0.5}}>📭</div>
            <div style={{fontSize: 16, fontWeight: 700}}>لا توجد أحداث بعد</div>
            <div style={{fontSize: 14, marginTop: 8}}>سيتم عرض الأحداث هنا عند بدء المهمة</div>
          </div>
        )}

        {events.map(ev => (
          <div 
            key={ev.id} 
            style={{
              marginBottom:14, 
              padding: 14, 
              background: 'rgba(16,26,47,0.6)', 
              borderRadius: 10,
              border: `1px solid ${getLevelColor(ev.level)}40`,
              borderLeft: `4px solid ${getLevelColor(ev.level)}`
            }}
          >
            <div className="row" style={{marginBottom: 8}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                <span style={{fontSize: 18}}>{getLevelIcon(ev.level)}</span>
                <div className="small" style={{color: getLevelColor(ev.level), fontWeight: 700}}>
                  {ev.level.toUpperCase()} / {ev.kind}
                </div>
              </div>
              <div className="small mono" style={{opacity: 0.7}}>{ev.ts}</div>
            </div>
            
            <div style={{fontSize: 14, lineHeight: 1.6, marginBottom: 8}}>
              {ev.message}
            </div>

            {ev.data?.output_text && (
              <pre 
                className="mono" 
                style={{
                  marginTop:10, 
                  padding:12, 
                  background:"rgba(11,18,32,0.8)", 
                  borderRadius:8, 
                  border:"1px solid rgba(148,163,184,0.18)",
                  maxHeight: 300,
                  overflow: 'auto',
                  fontSize: 12,
                  lineHeight: 1.5
                }}
              >
{String(ev.data.output_text)}
              </pre>
            )}
            
            {ev.data && !ev.data.output_text && Object.keys(ev.data).length > 0 && (
              <pre 
                className="mono" 
                style={{
                  marginTop:10, 
                  padding:12, 
                  background:"rgba(11,18,32,0.8)", 
                  borderRadius:8, 
                  border:"1px solid rgba(148,163,184,0.18)",
                  maxHeight: 300,
                  overflow: 'auto',
                  fontSize: 12,
                  lineHeight: 1.5
                }}
              >
{JSON.stringify(ev.data, null, 2)}
              </pre>
            )}
          </div>
        ))}
      </div>

      <div style={{marginTop: 16, padding: 12, background: 'rgba(124,58,237,0.1)', borderRadius: 8, border: '1px solid rgba(124,58,237,0.3)', textAlign: 'center'}}>
        <div className="small" style={{fontWeight: 600}}>
        </div>
      </div>
    </div>
  );
}
