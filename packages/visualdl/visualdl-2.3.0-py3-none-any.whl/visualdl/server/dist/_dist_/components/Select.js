import d,{useCallback as u,useEffect as P,useMemo as m,useState as A}from"../../__snowpack__/pkg/react.js";import{borderRadius as O,borderRadiusShortHand as _,css as g,ellipsis as z,em as $,math as W,sameBorder as q,size as j,transitionProps as f,zIndexes as F}from"../utils/style.js";import G from"./Checkbox.js";import J from"./Icon.js";import a from"../../__snowpack__/pkg/styled-components.js";import K from"../hooks/useClickOutside.js";import{useTranslation as Q}from"../../__snowpack__/pkg/react-i18next.js";import U from"../../__snowpack__/pkg/lodash/without.js";export const padding=$(10),height=$(36);const X=a.div`
    --height: ${height};
    --padding: ${padding};
    height: var(--height);
    line-height: calc(var(--height) - 2px);
    max-width: 100%;
    display: inline-block;
    position: relative;
    background-color: var(--background-color);
    ${q({radius:!0})}
    ${o=>o.opened?_("bottom","0"):""}
    ${f("border-color","background-color")}

    &:hover {
        border-color: var(--border-focused-color);
    }
`,Y=a.div`
    padding: var(--padding);
    display: inline-flex;
    ${j("100%")}
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    ${o=>o.selected?"":"color: var(--text-lighter-color)"}
    ${f("color")}
`,Z=a(J)`
    ${j($(14))}
    text-align: center;
    display: block;
    flex-shrink: 0;
    transform: rotate(${o=>o.opened?"180":"0"}deg) scale(${10/14});
    ${f("transform")}
`,C=a.span`
    flex-grow: 1;
    padding-right: ${$(10)};
    line-height: 1;
    ${z()}
`,V=a.div`
    position: absolute;
    ${o=>o.direction==="top"?{bottom:"100%",borderBottomColor:"var(--border-color)",boxShadow:"0 -5px 6px 0 rgba(0, 0, 0, 0.05)",..._("top",O)}:{top:"100%",borderTopColor:"var(--border-color)",boxShadow:"0 5px 6px 0 rgba(0, 0, 0, 0.05)",..._("bottom",O)}}
    width: calc(100% + 2px);
    max-height: ${W(`4.35 * ${height} + 2 * ${padding}`)};
    overflow-x: hidden;
    overflow-y: auto;
    left: -1px;
    padding: ${padding} 0;
    border: inherit;
    display: ${o=>o.opened?"block":"none"};
    z-index: ${F.component};
    line-height: 1;
    background-color: inherit;
    ${f(["border-color","color"])}
    ${o=>o.empty?{color:"var(--text-lighter-color)",textAlign:"center"}:""}
`,T=g`
    display: block;
    cursor: pointer;
    padding: 0 ${padding};
    ${j(height,"100%")}
    line-height: ${height};
    ${f(["color","background-color"])}
`,B=g`
    &:hover {
        background-color: var(--background-focused-color);
    }
`,ee=a.div`
    ${z()}
    ${T}
    ${o=>o.disabled?g`
                cursor: not-allowed;
            `:B}
    ${o=>{if(o.selected)return g`
                color: var(--select-selected-text-color);
            `;if(o.disabled)return g`
                color: var(--text-light-color);
            `}}
`,oe=a(G)`
    ${T}
    display: flex;
    align-items: center;
    ${o=>o.disabled?"":B}
`,te=({list:o,value:n,placeholder:I,direction:M,multiple:s,className:R,onChange:c})=>{const{t:v}=Q("common"),[p,E]=A(!1),L=u(()=>E(!p),[p]),k=u(()=>E(!1),[]),[r,x]=A(s?Array.isArray(n)?n:[]:n);P(()=>x(s?Array.isArray(n)?n:[]:n),[s,n]);const D=u(({value:e,disabled:t})=>{t||(x(e),c==null||c(e),k())},[k,c]),H=u(({value:e,disabled:t},b)=>{if(t)return;let l=r;b?l.includes(e)||(l=[...l,e]):l.includes(e)&&(l=U(l,e)),x(l),c==null||c(l)},[r,c]),N=K(k),i=m(()=>{var e;return(e=o==null?void 0:o.map(t=>["string","number"].includes(typeof t)?{value:t,label:t+""}:t))!=null?e:[]},[o]),S=m(()=>i.length===0,[i]),h=m(()=>!!(s?r&&r.length!==0:!(r==null||i.findIndex(e=>e.value===r)===-1)),[i,s,r]),y=u(e=>{var t,b;return(b=(t=i.find(l=>l.value===e))==null?void 0:t.label)!=null?b:""},[i]),w=m(()=>h?s?r.map(y).join(" / "):y(r):I||v("common:select"),[s,r,y,h,I,v]);return d.createElement(X,{ref:N,opened:p,className:R},d.createElement(Y,{onClick:L,selected:h,title:h&&w?String(w):""},d.createElement(C,null,w),d.createElement(Z,{opened:p,type:"chevron-down"})),d.createElement(V,{className:"list",opened:p,empty:S,direction:M},S?v("common:empty"):i.map((e,t)=>s?d.createElement(oe,{checked:r.includes(e.value),key:t,title:e.label,disabled:e.disabled,size:"small",onChange:b=>H(e,b)},e.label):d.createElement(ee,{selected:e.value===r,key:t,title:e.label,disabled:e.disabled,onClick:()=>D(e)},e.label))))};export default te;
