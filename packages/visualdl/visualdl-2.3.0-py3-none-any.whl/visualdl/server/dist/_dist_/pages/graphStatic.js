import G,{AsideSection as c}from"../components/Aside.js";import ce from"../components/GraphPage/GraphStatic.js";import e,{useCallback as a,useEffect as O,useMemo as v,useRef as J,useState as n}from"../../__snowpack__/pkg/react.js";import ie from"../components/Select.js";import{actions as me,selectors as pe}from"../store/index.js";import{primaryColor as he,rem as i,size as ue}from"../utils/style.js";import{useDispatch as de,useSelector as ge}from"../../__snowpack__/pkg/react-redux.js";import y from"../components/Button.js";import P from"../components/Checkbox.js";import fe from"../components/Content.js";import w from"../components/Field.js";import Ee from"../../__snowpack__/pkg/react-spinners/HashLoader.js";import Se from"../components/GraphPage/ModelPropertiesDialog.js";import we from"../components/GraphPage/NodeDocumentationSidebar.js";import je from"../components/GraphPage/NodePropertiesSidebar.js";import K from"../components/RadioButton.js";import ke from"../components/RadioGroup.js";import Ce from"../components/GraphPage/Search.js";import xe from"../components/Title.js";import _e from"../components/GraphPage/Uploader.js";import m from"../../__snowpack__/pkg/styled-components.js";import be from"../hooks/useRequest.js";import{useTranslation as De}from"../../__snowpack__/pkg/react-i18next.js";const Q=m(y)`
    width: 100%;
`,Ge=m(ie)`
    width: 100%;
`,ve=m.div`
    display: flex;
    justify-content: space-between;

    > * {
        flex: 1 1 auto;

        &:not(:last-child) {
            margin-right: ${i(20)};
        }
    }
`,ye=m(c)`
    max-height: calc(100% - ${i(40)});
    display: flex;
    flex-direction: column;

    &:not(:last-child) {
        padding-bottom: 0;
    }
`,Pe=m.div`
    ${ue("100%","100%")}
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overscroll-behavior: none;
    cursor: progress;
    font-size: ${i(16)};
    line-height: ${i(60)};
`,Fe=()=>{const{t:o}=De(["graph","common"]),F=de(),V=ge(pe.graph.model),l=J(null),p=J(null),[j,N]=n(V),h=a(t=>{F(me.graph.setModel(t)),N(t)},[F]),u=a(()=>{p.current&&(p.current.value="",p.current.click())},[]),X=a(t=>{const r=t.target;r&&r.files&&r.files.length&&h(r.files)},[h]),{data:s,loading:k}=be(j?null:"/graph/static_graph");O(()=>{var t;((t=s==null?void 0:s.data)==null?void 0:t.size)&&N([new File([s.data],s.filename||"unknown_model")])},[s]);const[C,Y]=n([]),[R,M]=n(""),Z=a(t=>{Y(t.graphs),M(t.selected||"")},[]),z=a(t=>{var r;M(t),(r=l.current)==null||r.changeGraph(t)},[]),[A,x]=n(""),[d,B]=n(!1),[$,H]=n({text:"",result:[]}),L=a(t=>{var r;x(t),(r=l.current)==null||r.search(t)},[]),T=a(t=>{var r;x(t.name),(r=l.current)==null||r.select(t)},[]),[g,ee]=n(!1),[f,te]=n(!0),[E,oe]=n(!1),[_,ne]=n(!1),[re,U]=n(null),[S,W]=n(null),[b,D]=n(null);O(()=>{x(""),H({text:"",result:[]})},[j,g,f,E]);const q=v(()=>d?null:e.createElement(Q,{type:"primary",rounded:!0,onClick:u},o("graph:change-model")),[o,u,d]),[I,le]=n(!1),ae=v(()=>!I||k?null:b?e.createElement(G,{width:i(360)},e.createElement(we,{data:b,onClose:()=>D(null)})):S?e.createElement(G,{width:i(360)},e.createElement(je,{data:S,onClose:()=>W(null),showNodeDocumentation:()=>{var t;return(t=l.current)==null?void 0:t.showNodeDocumentation(S)}})):e.createElement(G,{bottom:q},e.createElement(ye,null,e.createElement(Ce,{text:A,data:$,onChange:L,onSelect:T,onActive:()=>B(!0),onDeactive:()=>B(!1)})),!d&&e.createElement(e.Fragment,null,e.createElement(c,null,e.createElement(Q,{onClick:()=>{var t;return(t=l.current)==null?void 0:t.showModelProperties()}},o("graph:model-properties"))),C.length>1&&e.createElement(c,null,e.createElement(w,{label:o("graph:subgraph")},e.createElement(Ge,{list:C,value:R,onChange:z}))),e.createElement(c,null,e.createElement(w,{label:o("graph:display-data")},e.createElement("div",null,e.createElement(P,{checked:g,onChange:ee},o("graph:show-attributes"))),e.createElement("div",null,e.createElement(P,{checked:f,onChange:te},o("graph:show-initializers"))),e.createElement("div",null,e.createElement(P,{checked:E,onChange:oe},o("graph:show-node-names"))))),e.createElement(c,null,e.createElement(w,{label:o("graph:direction")},e.createElement(ke,{value:_,onChange:ne},e.createElement(K,{value:!1},o("graph:vertical")),e.createElement(K,{value:!0},o("graph:horizontal"))))),e.createElement(c,null,e.createElement(w,{label:o("graph:export-file")},e.createElement(ve,null,e.createElement(y,{onClick:()=>{var t;return(t=l.current)==null?void 0:t.export("png")}},o("graph:export-png")),e.createElement(y,{onClick:()=>{var t;return(t=l.current)==null?void 0:t.export("svg")}},o("graph:export-svg"))))))),[o,q,A,d,$,C,R,z,L,T,g,f,E,_,I,k,S,b]),se=v(()=>e.createElement(_e,{onClickUpload:u,onDropFiles:h}),[u,h]);return e.createElement(e.Fragment,null,e.createElement(xe,null,o("common:graph")),e.createElement(Se,{data:re,onClose:()=>U(null)}),e.createElement(fe,{aside:ae},k?e.createElement(Pe,null,e.createElement(Ee,{size:"60px",color:he})):e.createElement(ce,{ref:l,files:j,uploader:se,showAttributes:g,showInitializers:f,showNames:E,horizontal:_,onRendered:()=>le(!0),onOpened:Z,onSearch:t=>{H(t)},onShowModelProperties:t=>U(t),onShowNodeProperties:t=>{W(t),D(null)},onShowNodeDocumentation:t=>D(t)}),e.createElement("input",{ref:p,type:"file",multiple:!1,onChange:X,style:{display:"none"}})))};export default Fe;
