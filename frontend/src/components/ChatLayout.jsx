import React from "react";
import TopBar from "./TopBar";
import Sidebar from "./Sidebar";
import Composer from "./Composer";

export default function ChatLayout(){
  return (
    <div className="app" dir="rtl" style={{fontFamily:"var(--font-base)"}}>
      <TopBar/>
      <div className="layout" style={{display:"grid", gridTemplateColumns:"280px 1fr", gap:"var(--space-md)"}}>
        <Sidebar/>
        <main>
          <div className="conversation-area"> {/* messages go here */}</div>
          <Composer/>
        </main>
      </div>
    </div>
  );
}
