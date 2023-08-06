import e,{useCallback as c,useState as g}from"../../../__snowpack__/pkg/react.js";import{em as a,sameBorder as f,size as h,transitionProps as s}from"../../utils/style.js";import v from"../Button.js";import E from"../Icon.js";import p from"../../../__snowpack__/pkg/styled-components.js";import{useTranslation as y}from"../../../__snowpack__/pkg/react-i18next.js";const $=p.div`
    ${r=>f({width:"1px",type:"dashed",radius:a(16),color:r.active?"var(--primary-color)":void 0})}
    background-color: ${r=>r.active?"var(--graph-uploader-active-background-color)":"var(--graph-uploader-background-color)"};
    ${h("43.2%","68%")}
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    ${s("border-color","background-color")}

    > .upload-icon {
        font-size: ${a(64)};
        color: var(--primary-color);
        ${s("color")}
    }

    > span {
        font-size: ${a(18)};
        line-height: 3.2;
    }

    > .upload-button {
        min-width: ${a(155)};
    }
`,_=p.table`
    max-width: 68%;
    margin-top: ${a(32)};

    td {
        vertical-align: text-top;
        line-height: 2;

        &:first-of-type {
            color: var(--text-light-color);
            text-align: right;
            padding-right: ${a(10)};
            font-size: ${a(16)};
            width: ${a(250)};
            ${s("color")}
        }
    }
`,b=({onClickUpload:r,onDropFiles:n})=>{const{t:o}=y("graph"),[i,l]=g(!1),d=c(()=>r==null?void 0:r(),[r]),u=c(t=>{t.preventDefault(),l(!1),t.dataTransfer&&t.dataTransfer.files&&t.dataTransfer.files.length&&(n==null||n(t.dataTransfer.files))},[n]),m=c(t=>{t.preventDefault(),!t.currentTarget.contains(t.relatedTarget)&&l(!1)},[]);return e.createElement(e.Fragment,null,e.createElement($,{active:i,onDrop:u,onDragOver:t=>t.preventDefault(),onDragEnter:()=>l(!0),onDragLeave:m},e.createElement(E,{type:"upload",className:"upload-icon"}),e.createElement("span",null,o("graph:upload-tip")),e.createElement(v,{type:"primary",rounded:!0,className:"upload-button",onClick:d},o("graph:upload-model"))),e.createElement(_,null,e.createElement("tbody",null,e.createElement("tr",null,e.createElement("td",null,o("graph:supported-model")),e.createElement("td",null,o("graph:supported-model-list"))),e.createElement("tr",null,e.createElement("td",null,o("graph:experimental-supported-model")),e.createElement("td",null,o("graph:experimental-supported-model-list"))))))};export default b;
