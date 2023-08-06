import e from"../../__snowpack__/pkg/react.js";import{contentHeight as s,contentMargin as m,headerHeight as l,position as d,transitionProps as g}from"../utils/style.js";import p from"./BodyLoading.js";import t from"../../__snowpack__/pkg/styled-components.js";const u=t.section`
    display: flex;
`,h=t.article`
    flex: auto;
    min-width: 0;
    margin: ${m};
    min-height: ${s};
`,r=t.aside`
    flex: none;
    background-color: var(--background-color);
    height: ${`calc(100vh - ${l})`};
    ${d("sticky",l,0,null,null)}
    overflow-x: hidden;
    overflow-y: auto;
    ${g("background-color")}
`,f=({children:c,aside:o,leftAside:n,loading:i,className:a})=>e.createElement(u,{className:a},n&&e.createElement(r,null,n),e.createElement(h,null,c),o&&e.createElement(r,null,o),i&&e.createElement(p,null));export default f;
