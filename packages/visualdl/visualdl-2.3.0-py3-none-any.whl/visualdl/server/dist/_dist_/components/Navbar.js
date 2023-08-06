import*as k from"../../__snowpack__/env.js";import{Link as W,useLocation as q}from"../../__snowpack__/pkg/react-router-dom.js";import e,{useCallback as H,useEffect as V,useMemo as h,useState as z}from"../../__snowpack__/pkg/react.js";import{border as D,borderRadius as Y,rem as o,size as w,transitionProps as b,triangle as F}from"../utils/style.js";import $ from"./Icon.js";import X from"./Language.js";import G from"./ThemeToggle.js";import x from"../../__snowpack__/pkg/@tippyjs/react.js";import J from"../utils/event.js";import{getApiToken as Q}from"../utils/fetch.js";import Z from"../assets/images/logo.svg.proxy.js";import A from"../../__snowpack__/pkg/query-string.js";import g from"../../__snowpack__/pkg/styled-components.js";import ee from"../hooks/useClassNames.js";import te from"../hooks/useComponents.js";import{useTranslation as ne}from"../../__snowpack__/pkg/react-i18next.js";const L=k.SNOWPACK_PUBLIC_BASE_URI,ae=k.SNOWPACK_PUBLIC_PATH,P=k.SNOWPACK_PUBLIC_API_TOKEN_KEY,S=6,T=n=>{const a=[];return n.forEach(c=>{c.children?a.push(...T(c.children)):a.push(c)}),a};function U(n){if(!P)return n;const a=A.parseUrl(n);return A.stringifyUrl({...a,query:{...a.query,[P]:Q()}})}const re=g.nav`
    background-color: var(--navbar-background-color);
    color: var(--navbar-text-color);
    ${w("100%")}
    padding: 0 ${o(20)};
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    ${b(["background-color","color"])}

    > .left {
        display: flex;
        justify-content: flex-start;
        align-items: center;
    }

    > .right {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-right: -${o(20)};
    }
`,oe=g.a`
    font-size: ${o(20)};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif,
        'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
    font-weight: 600;
    margin-right: ${o(40)};

    > img {
        ${w(o(31),o(98))}
        vertical-align: middle;
        margin-right: ${o(8)};
    }

    > span {
        vertical-align: middle;
    }
`,u=g.div`
    height: 100%;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    background-color: var(--navbar-background-color);
    cursor: pointer;
    ${b("background-color")}

    &:hover {
        background-color: var(--navbar-hover-background-color);
    }

    &.nav-item {
        padding: 0 ${o(20)};
    }

    .nav-link {
        display: inline-block;
        width: 100%;
        height: 100%;
        display: inline-flex;
        justify-content: center;
        align-items: center;
    }

    .nav-text {
        margin: ${o(20)};
        padding: ${o(10)} 0 ${o(7)};
        ${n=>D("bottom",o(3),"solid",n.active?"var(--navbar-highlight-color)":"transparent")}
        ${b("border-bottom")}
        text-transform: uppercase;

        &.dropdown-icon {
            &::after {
                content: '';
                display: inline-block;
                width: 0;
                height: 0;
                margin-left: 0.5rem;
                vertical-align: middle;
                ${F({pointingDirection:"bottom",width:o(8),height:o(5),foregroundColor:"currentColor"})}
            }
        }
    }
`,O=g.div`
    overflow: hidden;
    border-radius: ${Y};
`,ce=g.div`
    display: block;
    line-height: 3em;

    &,
    &:visited {
        color: ${n=>n.active?"var(--primary-color)":"var(--text-color)"};
    }

    &:hover {
        background-color: var(--background-focused-color);
    }

    > a {
        display: block;
        padding: 0 ${o(20)};
    }
`,B=({to:n,children:a,...c})=>e.createElement(W,{to:n?U(n):"",...c},a),E=e.forwardRef(({path:n,active:a,showDropdownIcon:c,children:m},s)=>{const l=ee("nav-text",{"dropdown-icon":c},[c]);return n?e.createElement(u,{active:a,ref:s},e.createElement(B,{to:n,className:"nav-link"},e.createElement("span",{className:l},m))):e.createElement(u,{active:a,ref:s},e.createElement("span",{className:l},m))});E.displayName="NavbarItem";const K=({menu:n,active:a,path:c,showDropdownIcon:m,children:s})=>e.createElement(x,{placement:"bottom-start",animation:"shift-away-subtle",interactive:!0,arrow:!1,offset:[0,0],hideOnClick:!1,role:"menu",content:e.createElement(O,null,n.map(l=>e.createElement(ce,{active:l.active,key:l.id},e.createElement(B,{to:l.path},l.name))))},e.createElement(E,{active:a||!1,path:c,showDropdownIcon:m},s)),se=()=>{const{t:n,i18n:a}=ne("common"),{pathname:c}=q(),m=H(()=>{const t=a.language,r=(a.options.supportedLngs||[]).filter(v=>v!=="cimode"),i=r.indexOf(t),f=i<0||i>=r.length-1?r[0]:r[i+1];a.changeLanguage(f)},[a]),s=h(()=>c.replace(L,""),[c]),[l]=te(),y=h(()=>l.slice(0,S),[l]),N=h(()=>T(l.slice(S)),[l]),I=h(()=>N.map(t=>({...t,active:s===t.path})),[s,N]),[M,R]=z([]);return V(()=>{R(t=>y.map(r=>{var f,v,j,C;const i=(f=r.children)==null?void 0:f.map(p=>({...p,active:p.path===s}));if(r.children&&!r.path){const p=r.children.find(d=>d.path===s);if(p)return{...r,cid:p.id,name:p.name,path:s,active:!0,children:i};{const d=t.find(_=>_.id===r.id);if(d)return{...r,...d,name:(C=(j=(v=r.children)==null?void 0:v.find(_=>_.id===d.cid))==null?void 0:j.name)!=null?C:r.name,active:!1,children:i}}}return{...r,active:s===r.path,children:i}}))},[y,s]),e.createElement(re,null,e.createElement("div",{className:"left"},e.createElement(oe,{href:U(L+"/index")},e.createElement("img",{alt:"PaddlePaddle",src:ae+Z}),e.createElement("span",null,"VisualDL")),M.map(t=>t.children?e.createElement(K,{menu:t.children,active:t.active,path:t.path,key:t.active?`${t.id}-activated`:t.id},t.name):e.createElement(E,{active:t.active,path:t.path,key:t.id},t.name)),I.length?e.createElement(K,{menu:I,showDropdownIcon:!0},n("common:more")):null),e.createElement("div",{className:"right"},e.createElement(x,{placement:"bottom-end",animation:"shift-away-subtle",interactive:!0,arrow:!1,offset:[18,0],hideOnClick:!1,role:"menu",content:e.createElement(O,null,e.createElement(G,null))},e.createElement(u,{className:"nav-item"},e.createElement($,{type:"theme"}))),e.createElement(u,{className:"nav-item",onClick:m},e.createElement(X,null)),e.createElement(u,{className:"nav-item",onClick:()=>J.emit("refresh")},e.createElement($,{type:"refresh"}))))};export default se;
