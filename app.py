import streamlit as stimport streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")
st.title("🎯 Game Bắn Bóng (Bubble Shooter)")

parts = [
    "<!DOCTYPE html><html><head><meta charset='utf-8'>",
    "<style>body{margin:0;text-align:center;font-family:sans-serif;background:#0f0f1a;color:white;}",
    "canvas{background:#1e1e2e;display:block;margin:10px auto;border-radius:12px;box-shadow:0 8px 20px rgba(0,0,0,0.6);cursor:crosshair;}</style>",
    "</head><body><canvas id='c' width='440' height='540'></canvas><script>",
    "const cvs=document.getElementById('c'),ctx=cvs.getContext('2d');",
    "let score=0,shots=0,over=false,bullet=null,mx=220,my=0;",
    "const cols=['#FF5964','#35A7FF','#38B000','#FFE600','#9B5DE5'];",
    "const rC=()=>cols[Math.floor(Math.random()*cols.length)];",
    "let shooter={x:220,y:510,r:18,color:rC()};",
    "let bubbles=[],fallingBubbles=[],rad=18,dia=36,rH=31.176;",
    "function init(){bubbles=[];fallingBubbles=[];over=false;score=0;shots=0;",
    "for(let r=0;r<4;r++){let numC=(r%2===1)?9:10,offX=(r%2===1)?rad:0;",
    "for(let c=0;c<numC;c++)bubbles.push({row:r,col:c,x:25+rad+c*dia+offX,y:25+r*rH,r:rad,color:rC(),active:true});}}init();",
    "function addRow(){bubbles.forEach(b=>{b.y+=rH;b.row++;if(b.active&&b.y>=430)over=true;});",
    "for(let c=0;c<10;c++)bubbles.unshift({row:0,col:c,x:25+rad+c*dia,y:25,r:rad,color:rC(),active:true});}",
    "cvs.addEventListener('mousemove',e=>{if(over)return;let rct=cvs.getBoundingClientRect();mx=e.clientX-rct.left;my=e.clientY-rct.top;});",
    "cvs.addEventListener('click',()=>{if(over){init();return;}if(!bullet){let a=Math.atan2(my-shooter.y,mx-shooter.x);",
    "if(a>-0.1)a=-0.1;if(a<-Math.PI+0.1)a=-Math.PI+0.1;",
    "bullet={x:shooter.x,y:shooter.y,dx:Math.cos(a)*7,dy:Math.sin(a)*7,color:shooter.color};shooter.color=rC();}});",
    "function getNeighbors(r,c){return(r%2===0)?[{r:r-1,c:c-1},{r:r-1,c:c},{r:r,c:c-1},{r:r,c:c+1},{r:r+1,c:c-1},{r:r+1,c:c}]:[{r:r-1,c:c},{r:r-1,c:c+1},{r:r,c:c-1},{r:r,c:c+1},{r:r+1,c:c},{r:r+1,c:c+1}];}",
    "function snap(hitB,bCol){let target=null,nList=getNeighbors(hitB.row,hitB.col),iAngle=Math.atan2(bullet.y-hitB.y,bullet.x-hitB.x);",
    "let minDiff=Infinity;for(let n of nList){let maxC=(n.r%2===1)?9:10;if(n.r>=0&&n.r<15&&n.c>=0&&n.c<maxC){",
    "let occ=bubbles.some(b=>b.active&&b.row===n.r&&b.col===n.c);if(!occ){",
    "let offX=(n.r%2===1)?rad:0,tx=25+rad+n.c*dia+offX,ty=25+n.r*rH;",
    "let angleToN=Math.atan2(ty-hitB.y,tx-hitB.x),diff=Math.abs(iAngle-angleToN);",
    "if(diff>Math.PI)diff=Math.PI*2-diff;if(diff<minDiff){minDiff=diff;target={row:n.r,col:n.c,x:tx,y:ty};}}}}",
    "if(!target){let minD=Infinity;for(let n of nList){let maxC=(n.r%2===1)?9:10;if(n.r>=0&&n.r<15&&n.c>=0&&n.c<maxC){",
    "let occ=bubbles.some(b=>b.active&&b.row===n.r&&b.col===n.c);if(!occ){",
    "let offX=(n.r%2===1)?rad:0,tx=25+rad+n.c*dia+offX,ty=25+n.r*rH;",
    "let d=Math.hypot(bullet.x-tx,bullet.y-ty);if(d<minD){minD=d;target={row:n.r,col:n.c,x:tx,y:ty};}}}}}}",
    "if(!target){let minD=Infinity;for(let r=0;r<15;r++){let maxC=(r%2===1)?9:10;for(let c=0;c<maxC;c++){",
    "let occ=bubbles.some(b=>b.active&&b.row===r&&b.col===c);if(!occ){",
    "let offX=(r%2===1)?rad:0,tx=25+rad+c*dia+offX,ty=25+r*rH;",
    "let d=Math.hypot(bullet.x-tx,bullet.y-ty);if(d<minD){minD=d;target={row:r,col:c,x:tx,y:ty};}}}}}}",
    "if(!target){let r=Math.max(0,Math.min(14,Math.round((bullet.y-25)/rH)));",
    "let maxC=(r%2===1)?9:10,c=Math.max(0,Math.min(maxC-1,Math.round((bullet.x-25-rad-((r%2===1)?rad:0))/dia)));",
    "let offX=(r%2===1)?rad:0;target={row:r,col:c,x:25+rad+c*dia+offX,y:25+r*rH};}",
    "if(bubbles.some(b=>b.active&&b.row===target.row&&b.col===target.col)){",
    "for(let r=0;r<15;r++){let maxC=(r%2===1)?9:10,found=false;for(let c=0;c<maxC;c++){",
    "if(!bubbles.some(b=>b.active&&b.row===r&&b.col===c)){",
    "let offX=(r%2===1)?rad:0;target={row:r,col:c,x:25+rad+c*dia+offX,y:25+r*rH};found=true;break;}}if(found)break;}}",
    "let nb={row:target.row,col:target.col,x:target.x,y:target.y,r:rad,color:bCol,active:true};",
    "bubbles.push(nb);if(nb.y>=430){over=true;return;}",
    "if(match(nb,bCol)>0)floatCheck();else{shots++;if(shots>=5){addRow();shots=0;}}}",
    "function snapCeiling(bCol){let ac=Math.max(0,Math.min(9,Math.round((bullet.x-25-rad)/dia)));",
    "let tx=25+rad+ac*dia,ty=25;if(bubbles.some(b=>b.active&&b.row===0&&b.col===ac)){",
    "let minD=Infinity,bestC=ac;for(let c=0;c<10;c++){if(!bubbles.some(b=>b.active&&b.row===0&&b.col===c)){",
    "let d=Math.abs((25+rad+c*dia)-bullet.x);if(d<minD){minD=d;bestC=c;}}}ac=bestC;tx=25+rad+ac*dia;}",
    "if(bubbles.some(b=>b.active&&b.row===0&&b.col===ac)){",
    "for(let c=0;c<10;c++){if(!bubbles.some(b=>b.active&&b.row===0&&b.col===c)){ac=c;tx=25+rad+ac*dia;ak='ok';break;}}}",
    "let nb={row:0,col:ac,x:tx,y:ty,r:rad,color:bCol,active:true};bubbles.push(nb);",
    "if(match(nb,bCol)>0)floatCheck();else{shots++;if(shots>=5){addRow();shots=0;}}}",
    "function match(startB,tCol){let vis=new Set(),q=[startB],matched=[];vis.add(startB);",
    "while(q.length>0){let cur=q.shift();if(cur.color===tCol&&cur.active){matched.push(cur);",
    "let nList=getNeighbors(cur.row,cur.col);for(let n of nList){let nb=bubbles.find(b=>b.active&&!vis.has(b)&&b.row===n.r&&b.col===n.c);",
    "if(nb){vis.add(nb);q.push(nb);}}}}",
    "if(matched.length>=3){matched.forEach(b=>{b.active=false;score+=20;});return matched.length;}return 0;}",
    "function floatCheck(){let vis=new Set(),q=[];",
    "bubbles.forEach(b=>{if(b.active&&b.row===0){vis.add(b);q.push(b);}});",
    "while(q.length>0){let cur=q.shift();let nList=getNeighbors(cur.row,cur.col);",
    "for(let n of nList){let nb=bubbles.find(b=>b.active&&!vis.has(b)&&b.row===n.r&&b.col===n.c);",
    "if(nb){vis.add(nb);q.push(nb);}}}",
    "bubbles.forEach(b=>{if(b.active&&!vis.has(b)){b.active=false;score+=30;",
    "fallingBubbles.push({x:b.x,y:b.y,r:rad,color:b.color,dx:(Math.random()-0.5)*4,dy:2+Math.random()*2});}});}",
    "function update(){if(over)return;if(bullet){bullet.x+=bullet.dx;bullet.y+=bullet.dy;",
    "if(bullet.x-rad<0||bullet.x+rad>cvs.width)bullet.dx*=-1;",
    "if(bullet.y-rad<=15){snapCeiling(bullet.color);bullet=null;return;}",
    "for(let b of bubbles){if(b.active&&Math.hypot(bullet.x-b.x,bullet.y-b.y)<=dia){snap(b,bullet.color);bullet=null;break;}}}",
    "fallingBubbles.forEach(fb=>{fb.y+=fb.dy;fb.x+=fb.dx;fb.dy+=0.5;});fallingBubbles=fallingBubbles.filter(fb=>fb.y<cvs.height+50);}",
    "function draw(){ctx.clearRect(0,0,cvs.width,cvs.height);ctx.fillStyle='#FFF';ctx.font='bold 16px sans-serif';",
    "ctx.fillText('Điểm: '+score,20,25);ctx.fillText('Chờ hàng: '+(5-shots),310,25);",
    "bubbles.forEach(b=>{if(b.active){ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,Math.PI*2);ctx.fillStyle=b.color;ctx.fill();",
    "ctx.lineWidth=2;ctx.strokeStyle='rgba(255,255,255,0.25)';ctx.stroke();ctx.closePath();}});",
    "fallingBubbles.forEach(fb=>{ctx.beginPath();ctx.arc(fb.x,fb.y,fb.r,0,Math.PI*2);ctx.fillStyle=fb.color;ctx.fill();",
    "ctx.lineWidth=2;ctx.strokeStyle='rgba(255,255,255,0.25)';ctx.stroke();ctx.closePath();});",
    "if(!over){let a=Math.atan2(my-shooter.y,mx-shooter.x),rx=shooter.x,ry=shooter.y,rdx=Math.cos(a),rdy=Math.sin(a);",
    "ctx.beginPath();ctx.moveTo(rx,ry);for(let i=0;i<400;i++){rx+=rdx*3;ry+=rdy*3;",
    "if(rx-rad<0){rx=rad;rdx*=-1;ctx.lineTo(rx,ry);}else if(rx+rad>cvs.width){rx=cvs.width-rad;rdx*=-1;ctx.lineTo(rx,ry);}",
    "if(ry<=25){ctx.lineTo(rx,ry);break;}",
    "if(bubbles.some(b=>b.active&&Math.hypot(rx-b.x,ry-b.y)<rad*1.8)){ctx.lineTo(rx,ry);break;}}",
    "ctx.lineTo(rx,ry);ctx.strokeStyle='rgba(255,255,255,0.6)';ctx.setLineDash([4,4]);ctx.stroke();ctx.setLineDash([]);}",
    "if(bullet){ctx.beginPath();ctx.arc(bullet.x,bullet.y,rad,0,Math.PI*2);ctx.fillStyle=bullet.color;ctx.fill();ctx.closePath();}",
    "ctx.beginPath();ctx.arc(shooter.x,shooter.y,shooter.r,0,Math.PI*2);ctx.fillStyle=shooter.color;ctx.fill();",
    "ctx.lineWidth=3;ctx.strokeStyle='#FFF';ctx.stroke();ctx.closePath();",
    "if(over){ctx.fillStyle='rgba(0,0,0,0.85)';ctx.fillRect(0,0,cvs.width,cvs.height);",
    "ctx.fillStyle='#FF5964';ctx.font='bold 32px sans-serif';ctx.textAlign='center';ctx.fillText('GAME OVER',cvs.width/2,cvs.height/2-20);",
    "ctx.fillStyle='#FFF';ctx.font='18px sans-serif';ctx.fillText('Tổng điểm: '+score,cvs.width/2,cvs.height/2+20);",
    "ctx.fillText('Click chuột để chơi lại',cvs.width/2,cvs.height/2+60);ctx.textAlign='left';}}",
    "function loop(){update();draw();requestAnimationFrame(loop);}loop();</script></body></html>"
]

html_code = "".join(parts)
encoded_html = base64.b64encode(html_code.encode("utf-8")).decode("utf-8")
components.iframe(f"data:text/html;base64,{encoded_html}", height=580)
            bubbles.push(nb);
            if (match(nb, bCol) > 0) { floatCheck(); }
            else { shots++; if (shots >= 5) { addRow(); shots = 0; } }
        }

        function match(startB, tCol) {
            let vis = new Set(), q = [startB], matched = [];
            vis.add(startB);
            while (q.length > 0) {
                let cur = q.shift();
                if (cur.color === tCol && cur.active) {
                    matched.push(cur);
                    let nList = getNeighbors(cur.row, cur.col);
                    for (let n of nList) {
                        let nb = bubbles.find(b => b.active && !vis.has(b) && b.row === n.r && b.col === n.c);
                        if (nb) { vis.add(nb); q.push(nb); }
                    }
                }
            }
            if (matched.length >= 3) {
                matched.forEach(b => { b.active = false; score += 20; });
                return matched.length;
            }
            return 0;
        }

        function floatCheck() {
            let vis = new Set(), q = [];
            bubbles.forEach(b => { if (b.active && b.row === 0) { vis.add(b); q.push(b); } });
            while (q.length > 0) {
                let cur = q.shift();
                let nList = getNeighbors(cur.row, cur.col);
                for (let n of nList) {
                    let nb = bubbles.find(b => b.active && !vis.has(b) && b.row === n.r && b.col === n.c);
                    if (nb) { vis.add(nb); q.push(nb); }
                }
            }
            bubbles.forEach(b => {
                if (b.active && !vis.has(b)) {
                    b.active = false;
                    score += 30;
                    fallingBubbles.push({ x: b.x, y: b.y, r: rad, color: b.color, dx: (Math.random() - 0.5) * 4, dy: 2 + Math.random() * 2 });
                }
            });
        }

        function update() {
            if (over) return;
            if (bullet) {
                bullet.x += bullet.dx;
                bullet.y += bullet.dy;
                if (bullet.x - rad < 0 || bullet.x + rad > cvs.width) bullet.dx *= -1;
                if (bullet.y - rad <= 15) {
                    snapCeiling(bullet.color);
                    bullet = null;
                    return;
                }
                for (let b of bubbles) {
                    if (b.active && Math.hypot(bullet.x - b.x, bullet.y - b.y) <= dia) {
                        snap(b, bullet.color);
                        bullet = null;
                        break;
                    }
                }
            }
            fallingBubbles.forEach(fb => {
                fb.y += fb.dy;
                fb.x += fb.dx;
                fb.dy += 0.5;
            });
            fallingBubbles = fallingBubbles.filter(fb => fb.y < cvs.height + 50);
        }

        function draw() {
            ctx.clearRect(0, 0, cvs.width, cvs.height);
            ctx.fillStyle = "#FFF";
            ctx.font = "bold 16px sans-serif";
            ctx.fillText("Điểm: " + score, 20, 25);
            ctx.fillText("Chờ hàng: " + (5 - shots), 310, 25);

            bubbles.forEach(b => {
                if (b.active) {
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                    ctx.fillStyle = b.color;
                    ctx.fill();
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = "rgba(255,255,255,0.25)";
                    ctx.stroke();
                    ctx.closePath();
                }
            });

            fallingBubbles.forEach(fb => {
                ctx.beginPath();
                ctx.arc(fb.x, fb.y, fb.r, 0, Math.PI * 2);
                ctx.fillStyle = fb.color;
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = "rgba(255,255,255,0.25)";
                ctx.stroke();
                ctx.closePath();
            });

            if (!over) {
                let a = Math.atan2(my - shooter.y, mx - shooter.x);
                let rx = shooter.x, ry = shooter.y, rdx = Math.cos(a), rdy = Math.sin(a);
                ctx.beginPath();
                ctx.moveTo(rx, ry);
                for (let i = 0; i < 400; i++) {
                    rx += rdx * 3; ry += rdy * 3;
                    if (rx - rad < 0) { rx = rad; rdx *= -1; ctx.lineTo(rx, ry); }
                    else if (rx + rad > cvs.width) { rx = cvs.width - rad; rdx *= -1; ctx.lineTo(rx, ry); }
                    if (ry <= 25) { ctx.lineTo(rx, ry); break; }
                    let hit = bubbles.some(b => b.active && Math.hypot(rx - b.x, ry - b.y) < rad * 1.8);
                    if (hit) { ctx.lineTo(rx, ry); break; }
                }
                ctx.lineTo(rx, ry);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
                ctx.setLineDash([4, 4]);
                ctx.stroke();
                ctx.setLineDash([]);
            }

            if
