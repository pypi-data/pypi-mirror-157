import{useCallback as n,useEffect as g,useLayoutEffect as h,useMemo as L,useRef as a,useState as S}from"../../__snowpack__/pkg/react.js";import{position as k,primaryColor as v,size as _}from"../utils/style.js";import{dataURL2Blob as T}from"../utils/image.js";import{saveFile as j}from"../utils/saveFile.js";import w from"../../__snowpack__/pkg/styled-components.js";import{themes as d}from"../utils/theme.js";import f from"./useTheme.js";const A=t=>{const l=a(null),[o,c]=S(null),u=f(),m=a(t.onInit),x=a(t.onDispose),s=n(()=>o==null?void 0:o.dispatchAction({type:"hideTip"}),[o]),p=n(()=>{(async()=>{if(!l.current)return;const{default:r}=await import("../../__snowpack__/pkg/echarts.js");t.gl&&await import("../../__snowpack__/pkg/echarts-gl.js");const e=r.init(l.current);l.current.addEventListener("mouseleave",s),setTimeout(()=>{var i;t.zoom&&e.dispatchAction({type:"takeGlobalCursor",key:"dataZoomSelect",dataZoomSelectActive:!0}),e&&((i=m.current)==null||i.call(m,e))},0),c(e)})()},[t.gl,t.zoom,s]),C=n(()=>{var r,e;o&&((r=x.current)==null||r.call(x,o),o.dispose(),(e=l.current)==null||e.removeEventListener("mouseleave",s),c(null))},[s,o]);g(()=>(p(),C),[p,C]),g(()=>{t.loading?o==null||o.showLoading("default",{text:"",color:v,textColor:d[u].textColor,maskColor:d[u].maskColor,zlevel:0}):o==null||o.hideLoading()},[t.loading,u,o]);const y=a(null);h(()=>{if(t.autoFit){const r=y.current;if(r){let e=null;const i=new ResizeObserver(()=>{e!=null&&(cancelAnimationFrame(e),e=null),e=requestAnimationFrame(()=>{o==null||o.resize()})});return i.observe(r),()=>i.unobserve(r)}}},[t.autoFit,o]);const b=n(r=>{if(o){const e=T(o.getDataURL({type:"png",pixelRatio:2,backgroundColor:"#FFF"}));j(e,`${r||"chart"}.png`)}},[o]);return{ref:l,echart:o,wrapper:y,saveAsImage:b}};export default A;export const Wrapper=w.div`
    position: relative;
    display: flex;
    justify-content: center;
    align-items: stretch;

    > .echarts {
        width: 100%;
    }

    > .loading {
        ${_("100%")}
        ${k("absolute",0,null,null,0)}
        display: flex;
        justify-content: center;
        align-items: center;
    }
`,useChartTheme=t=>{const l=f(),o=L(()=>d[l],[l]);return L(()=>t?{title:{textStyle:{color:o.textColor}},tooltip:{backgroundColor:o.tooltipBackgroundColor,borderColor:o.tooltipBackgroundColor,textStyle:{color:o.tooltipTextColor}},xAxis3D:{nameTextStyle:{color:o.textLightColor},axisLabel:{color:o.textLightColor},axisLine:{lineStyle:{color:o.borderColor}},splitLine:{lineStyle:{color:o.borderColor}}},yAxis3D:{nameTextStyle:{color:o.textLightColor},axisLabel:{color:o.textLightColor},axisLine:{lineStyle:{color:o.borderColor}},splitLine:{lineStyle:{color:o.borderColor}}},zAxis3D:{nameTextStyle:{color:o.textLightColor},axisLabel:{color:o.textLightColor},axisLine:{lineStyle:{color:o.borderColor}},splitLine:{lineStyle:{color:o.borderColor}}}}:{title:{textStyle:{color:o.textColor}},tooltip:{backgroundColor:o.tooltipBackgroundColor,borderColor:o.tooltipBackgroundColor,textStyle:{color:o.tooltipTextColor}},xAxis:{nameTextStyle:{color:o.textLightColor},axisLabel:{color:o.textLightColor},axisLine:{lineStyle:{color:o.borderColor}},splitLine:{lineStyle:{color:o.borderColor}}},yAxis:{nameTextStyle:{color:o.textLightColor},axisLabel:{color:o.textLightColor},axisLine:{lineStyle:{color:o.borderColor}},splitLine:{lineStyle:{color:o.borderColor}}}},[o,t])};
