function beijingDay(date){return new Date(date.getTime()+8*3600000).toISOString().slice(0,10);}
/* Offline container adapter. ES2017; no network or navigation. */
(function () {
  'use strict';
  var cache = Object.create(null), queues = Object.create(null), api = null, version = 0;
  var keys = ['flowmate_saved','flowmate_profile','flowmate_eligibility_answers','flowmate_future_plans'];
  function notify(text) { var box=document.getElementById('toast'); if(!box)return; box.textContent=text;box.classList.add('show');clearTimeout(window._toast);window._toast=setTimeout(function(){box.classList.remove('show');},3000); }
  function parse(raw, fallback) { try { var value=JSON.parse(raw);return value==null?fallback:value; } catch(error) {return fallback;} }
  function supported(name, minimum) {return version>=minimum && api && typeof api[name]==='function';}
  window.FMStorage={
    read:function(key,fallback){return parse(cache[key],fallback);},
    write:function(key,value){
      var data;try{data=JSON.stringify(value);}catch(error){notify('未能保存，本次修改仅在当前页面有效');return false;}
      cache[key]=data;
      if(supported('setStorage',9460)) {
        queues[key]=(queues[key]||Promise.resolve()).catch(function(){}).then(function(){return api.setStorage({key:key,data:data});}).then(function(){notify('已保存到小工具本地缓存');},function(){notify('保存失败，本次修改仅在当前页面有效');});
        return false; // Async acknowledgment is shown only after actual success.
      }
      try{localStorage.setItem(key,data);return true;}catch(error){notify('当前环境无法保存，本次修改仅在当前页面有效');return false;}
    }
  };
  window.observeSize=function(element,callback){if(typeof ResizeObserver==='function'){new ResizeObserver(callback).observe(element);}else{window.addEventListener('resize',callback);setTimeout(callback,0);}};
  window.formValues=function(form){var result={};new FormData(form).forEach(function(value,key){result[key]=value;});return result;};
  // replaceChildren is not present in Chrome 61. append/prepend are supported.
  [window.Element,window.DocumentFragment].forEach(function(Type){if(Type&&!Type.prototype.replaceChildren){Type.prototype.replaceChildren=function(){while(this.firstChild)this.removeChild(this.firstChild);for(var i=0;i<arguments.length;i++)this.append(arguments[i]);};}});
  window.setBackgroundInert=function(value){var app=document.querySelector('.app');if('inert' in app)app.inert=value;app.setAttribute('aria-hidden',String(value));app.style.pointerEvents=value?'none':'';};
  var pendingFrame=null, frameRequested=false;
  window.scheduleOrbitFrame=function(callback){pendingFrame=callback;if(document.hidden||frameRequested)return;frameRequested=true;requestAnimationFrame(function(now){frameRequested=false;if(!document.hidden&&pendingFrame)pendingFrame(now);});};
  document.addEventListener('visibilitychange',function(){if(!document.hidden&&pendingFrame)window.scheduleOrbitFrame(pendingFrame);});
  function normalizeLinks(root){var links=[];if(root.nodeType===1&&root.tagName==='A')links.push(root);if(root.querySelectorAll)links=links.concat(Array.from(root.querySelectorAll('a')));links.forEach(function(link){var href=link.getAttribute('href');if(href&&/^https?:\/\//i.test(href)){link.dataset.reference=href;link.removeAttribute('href');link.removeAttribute('target');link.setAttribute('role','button');link.tabIndex=0;}});}
  // Source notices remain viewable as text; opening external pages is unavailable.
  var ref=document.createElement('div');ref.className='future-overlay';ref.id='referenceOverlay';ref.setAttribute('aria-hidden','true');
  var dialog=document.createElement('section');dialog.className='future-dialog';dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-label','来源参考');
  var title=document.createElement('h2');title.textContent='来源参考';var reminder=document.createElement('p');reminder.textContent='测试版 · 资料更新于2026年10月27日。小工具内无法打开外部网站；请通过主办方官网核实最新报名通知。';var address=document.createElement('p');address.className='source-address';var close=document.createElement('button');close.textContent='关闭';close.type='button';dialog.append(title,reminder,address,close);ref.append(dialog);document.body.append(ref);var previous=null;
  function closeReference(){ref.classList.remove('open');ref.setAttribute('aria-hidden','true');if(previous)previous.focus();}
  close.addEventListener('click',closeReference);ref.addEventListener('click',function(e){if(e.target===ref)closeReference();});
  function openReference(link){normalizeLinks(link);if(!link.dataset.reference)return;previous=link;address.textContent=link.dataset.reference;ref.classList.add('open');ref.setAttribute('aria-hidden','false');close.focus();}
  document.addEventListener('click',function(e){var link=e.target.closest('a');if(link){normalizeLinks(link);if(link.dataset.reference){e.preventDefault();e.stopImmediatePropagation();openReference(link);}}},true);
  document.addEventListener('keydown',function(e){if(ref.classList.contains('open')){if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();closeReference();}else if(e.key==='Tab'){e.preventDefault();e.stopImmediatePropagation();close.focus();}return;}var link=e.target.closest('a');if(link&&link.dataset.reference&&(e.key==='Enter'||e.key===' ')){e.preventDefault();openReference(link);}},true);
  new MutationObserver(function(records){records.forEach(function(record){if(record.type==='attributes')normalizeLinks(record.target);else Array.from(record.addedNodes).forEach(normalizeLinks);});}).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['href']});normalizeLinks(document);
  async function windowInfo(){
    document.documentElement.style.setProperty('--app-height',innerHeight+'px');
    if(!supported('getWindowInfo',9490))return;
    try{var info=await api.getWindowInfo(),area=info.safeArea;if(!area)return;var top=Math.max(0,area.top),buttons=info.menuButtons||{};Object.keys(buttons).forEach(function(key){var rect=buttons[key];if(rect&&rect.top<info.windowHeight/3)top=Math.max(top,rect.bottom);});var values={top:top,bottom:Math.max(0,info.windowHeight-area.bottom),left:Math.max(0,area.left),right:Math.max(0,info.windowWidth-area.right)};Object.keys(values).forEach(function(key){if(Number.isFinite(values[key]))document.documentElement.style.setProperty('--safe-area-inset-'+key,values[key]+'px');});}catch(error){}
  }
  window.addEventListener('resize',windowInfo);
  window.FMReady=(async function(){
    api=window.xhs&&window.xhs.miniTool;var launch=window.xhs&&window.xhs.launchOptions;
    if((!launch||!launch.miniToolEnv)&&api&&typeof api.getLaunchOptions==='function'){try{launch=await api.getLaunchOptions();}catch(error){}}
    var build=launch&&launch.miniToolEnv&&launch.miniToolEnv.buildVersion;version=Number.isFinite(Number(build))?Math.floor(Number(build)/1000):0;
    await Promise.all(keys.map(async function(key){try{if(supported('getStorage',9460)){var result=await api.getStorage({key:key});cache[key]=result&&result.data;}else{cache[key]=localStorage.getItem(key);}}catch(error){cache[key]=null;}}));
    await windowInfo();
  })();
})();
(function(){
  var probe=document.createElement('div');probe.style.cssText='display:flex;flex-direction:column;row-gap:1px;position:absolute;visibility:hidden';probe.append(document.createElement('div'),document.createElement('div'));document.body.append(probe);var hasGap=probe.scrollHeight===1;probe.remove();if(hasGap)return;
  function apply(){Array.from(document.querySelectorAll('body *')).forEach(function(parent){var style=getComputedStyle(parent);if(style.display!=='flex'&&style.display!=='inline-flex')return;var row=parseFloat(style.rowGap||style.gridRowGap)||0,col=parseFloat(style.columnGap||style.gridColumnGap)||0;if(!row&&!col)return;var vertical=style.flexDirection.indexOf('column')===0;Array.from(parent.children).forEach(function(child,index){if(index){if(vertical&&row)child.style.marginTop=row+'px';if(!vertical&&col)child.style.marginLeft=col+'px';if(!vertical&&style.flexWrap==='wrap'&&row)child.style.marginBottom=row+'px';}});});}
  var scheduled=false;function schedule(){if(scheduled)return;scheduled=true;setTimeout(function(){scheduled=false;apply();},40);}
  new MutationObserver(schedule).observe(document.body,{subtree:true,childList:true});window.addEventListener('resize',schedule);schedule();
})();
