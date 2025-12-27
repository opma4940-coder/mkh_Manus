import { useEffect, useState, useRef } from "react";
import { listWorkspace, readWorkspaceFile, uploadFile, uploadImage, uploadVideo, uploadAudio } from "../api";

export function WorkspacePanel(){
  const [path, setPath] = useState(".");
  const [tree, setTree] = useState<any>(null);
  const [filePath, setFilePath] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);

  async function refresh(p: string){
    try{
      const t = await listWorkspace(p);
      setTree(t);
    }catch(e){
      console.error(e);
    }
  }

  useEffect(()=>{
    refresh(path).catch(()=>{});
  }, [path]);

  async function openFile(p: string){
    try{
      const r = await readWorkspaceFile(p);
      setFilePath(p);
      setFileContent(r.content || "");
    }catch(e){
      console.error(e);
    }
  }

  async function handleFileUpload(file: File, type: 'file' | 'image' | 'video' | 'audio'){
    setUploading(true);
    setUploadStatus(null);
    try{
      let result;
      switch(type){
        case 'image':
          result = await uploadImage(file);
          break;
        case 'video':
          result = await uploadVideo(file);
          break;
        case 'audio':
          result = await uploadAudio(file);
          break;
        default:
          result = await uploadFile(file);
      }
      
      if(result.ok){
        setUploadStatus(`✅ تم رفع الملف بنجاح: ${result.path}`);
        await refresh(path);
      }
    }catch(e: any){
      setUploadStatus(`❌ فشل رفع الملف: ${e.message}`);
    }finally{
      setUploading(false);
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'file' | 'image' | 'video' | 'audio') => {
    const file = e.target.files?.[0];
    if(file){
      handleFileUpload(file, type);
    }
    e.target.value = '';
  };

  return (
    <div className="panel">
      <div className="row">
        <div style={{fontWeight:800, fontSize: 20}}>📂 مساحة العمل</div>
        <div className="small mono">Root: workspace/</div>
      </div>

      <div style={{marginTop:16}}>
        <div className="small" style={{marginBottom: 6}}>المسار الحالي</div>
        <div className="row">
          <input className="input" value={path} onChange={(e)=>setPath(e.target.value)} style={{flex: 1}} />
          <button className="btn secondary" onClick={()=>refresh(path)} disabled={uploading}>
          </button>
        </div>
      </div>

      <div style={{marginTop: 20, padding: 16, background: 'rgba(124,58,237,0.1)', borderRadius: 12, border: '1px solid rgba(124,58,237,0.3)'}}>
        <div style={{fontWeight: 700, marginBottom: 12, fontSize: 15}}>📤 رفع الملفات</div>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10}}>
          <button 
            className="btn" 
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8}}
          >
            <span style={{fontSize: 18}}>📄</span>
            <span>رفع ملف</span>
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            style={{display: 'none'}} 
            onChange={(e) => handleFileInputChange(e, 'file')}
          />

          <button 
            className="btn" 
            onClick={() => imageInputRef.current?.click()}
            disabled={uploading}
            style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, background: 'linear-gradient(135deg, #10b981, #059669)'}}
          >
            <span style={{fontSize: 18}}>🖼️</span>
            <span>رفع صورة</span>
          </button>
          <input 
            type="file" 
            ref={imageInputRef} 
            style={{display: 'none'}} 
            accept="image/*"
            onChange={(e) => handleFileInputChange(e, 'image')}
          />

          <button 
            className="btn" 
            onClick={() => videoInputRef.current?.click()}
            disabled={uploading}
            style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, background: 'linear-gradient(135deg, #f59e0b, #d97706)'}}
          >
            <span style={{fontSize: 18}}>🎥</span>
            <span>رفع فيديو</span>
          </button>
          <input 
            type="file" 
            ref={videoInputRef} 
            style={{display: 'none'}} 
            accept="video/*"
            onChange={(e) => handleFileInputChange(e, 'video')}
          />

          <button 
            className="btn" 
            onClick={() => audioInputRef.current?.click()}
            disabled={uploading}
            style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, background: 'linear-gradient(135deg, #3b82f6, #2563eb)'}}
          >
            <span style={{fontSize: 18}}>🎵</span>
            <span>رفع صوت</span>
          </button>
          <input 
            type="file" 
            ref={audioInputRef} 
            style={{display: 'none'}} 
            accept="audio/*"
            onChange={(e) => handleFileInputChange(e, 'audio')}
          />
        </div>
        
        {uploading && (
          <div style={{marginTop: 12, textAlign: 'center', color: 'var(--accent)', fontWeight: 600}}>
            ⏳ جاري رفع الملف...
          </div>
        )}
        
        {uploadStatus && (
          <div style={{marginTop: 12, padding: 10, background: 'rgba(11,18,32,0.6)', borderRadius: 8, fontSize: 13}}>
            {uploadStatus}
          </div>
        )}
      </div>

      <div className="split" style={{marginTop:20}}>
        <div style={{border:"1px solid rgba(148,163,184,0.18)", borderRadius:12, padding:16, maxHeight: 500, overflow:"auto", background: 'rgba(11,18,32,0.3)'}}>
          <div style={{fontWeight: 700, marginBottom: 12, fontSize: 15}}>📁 قائمة الملفات</div>
          <div className="list">
            {(Array.isArray(tree) ? tree : tree?.items || []).map((it:any)=>(
              <div key={it.path} className="item" onClick={()=>{
                if(it.is_dir) setPath(it.path);
                else openFile(it.path);
              }}>
                <div className="row">
                  <div className="mono" style={{fontWeight:800, fontSize: 16}}>
                    {it.is_dir ? "📁" : "📄"} {it.name}
                  </div>
                  <div className="small">{it.size_bytes} bytes</div>
                </div>
                <div className="small mono" style={{marginTop: 4}}>{it.path}</div>
              </div>
            ))}
            {(Array.isArray(tree) ? tree : tree?.items || []).length === 0 && (
              <div style={{textAlign: 'center', padding: 30, color: 'var(--muted)'}}>
                لا توجد ملفات في هذا المجلد
              </div>
            )}
          </div>
        </div>

        <div style={{border:"1px solid rgba(148,163,184,0.18)", borderRadius:12, padding:16, maxHeight: 500, overflow:"auto", background: 'rgba(11,18,32,0.3)'}}>
          <div style={{fontWeight: 700, marginBottom: 12, fontSize: 15}}>📄 عارض الملفات</div>
          <div className="small mono" style={{marginBottom: 10, padding: 8, background: 'rgba(124,58,237,0.1)', borderRadius: 6}}>
            {filePath || "اختر ملفاً من القائمة"}
          </div>
          {fileContent ? (
            <pre className="mono" style={{marginTop:10, maxHeight: 400, overflow: 'auto'}}>{fileContent}</pre>
          ) : (
            <div style={{textAlign: 'center', padding: 40, color: 'var(--muted)'}}>
              <div style={{fontSize: 48, marginBottom: 12}}>📄</div>
              <div>انقر على ملف لعرض محتواه</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
