function WrappingAscorinaion(){
    var editorArray = [];

    

    function Editor(opts){
        if(opts){
        this.init(opts);
        }
    }

    Editor.prototype.init =  function(opts){
        this.opts = opts;
        this.data = JSON.parse(popAttribute(opts,"data"));
        this.id = opts.id;
    }

    Editor.prototype.funkcija = function(group){
        
        // nesto
    }


    function popAttribute(element, atribute, fallback){
        var atr = fallback;
        if (element.hasAttribute(atribute)){
            atr = element.getAttribute(atribute);
            element.removeAttribute(atribute);
        }
        return atr;
    }

    window.addEventListener('load',function() {
        var editors = document.getElementsByClassName('petlja-editor');
        for (var i = 0; i < editors.length; i++) {
            editorArray[i] = new Editor(editors[i]);		
        }

        editorArray.forEach(editor => {
            if (editor.data.hasOwnProperty('js')) {
                var jsDiv = document.createElement('div');
                jsDiv.setAttribute('class', 'editor-container');
                var editorTitle = '<label class="editor-title">' + editor.data['js'].name  + '</h3>'
                jsDiv.innerHTML = editorTitle;
                document.getElementById(editor.id).append(jsDiv);
                var jsCodeMirror = CodeMirror(jsDiv, {
                    value: editor.data['js'].source,
                    mode:  "javascript",
                    lineNumbers: true,
                  });
                  jsCodeMirror.setSize(null,275);
                editor.jsEditor  = jsCodeMirror;
            }
            if (editor.data.hasOwnProperty('css')) {
                var cssDiv = document.createElement('div');
                cssDiv.setAttribute('class', 'editor-container');
                var editorTitle = '<label class="editor-title">' + editor.data['css'].name  + '</h3>'
                cssDiv.innerHTML = editorTitle;
                document.getElementById(editor.id).append(cssDiv);
                var cssCodeMirror = CodeMirror(cssDiv, {
                    value: editor.data['css'].source,
                    mode:  "css",
                    lineNumbers: true
                  });
                  cssCodeMirror.setSize(null,275);
                  editor.cssEditor  = cssCodeMirror;
            }
            if (editor.data.hasOwnProperty('html')) {
                var htmlDiv = document.createElement('div');
                htmlDiv.setAttribute('class', 'editor-container');
                var editorTitle = '<label class="editor-title">' + editor.data['html'].name  + '</h3>'
                htmlDiv.innerHTML = editorTitle;
                document.getElementById(editor.id).append(htmlDiv);
                var htmlCodeMirror = CodeMirror(htmlDiv, {
                    value: editor.data['html'].source,
                    mode:  "htmlmixed",
                    lineNumbers: true
                  });
                  htmlCodeMirror.setSize(null,275);
                  editor.htmlEditor  = htmlCodeMirror;
            }

                var htmliframe = document.createElement('iframe');
                htmliframe.setAttribute('class', 'editor-iframe');
                htmliframe.setAttribute('id', editor.id + "-iframe");
                document.getElementById(editor.id).append(htmliframe);
                
            var playBtn = document.createElement('div');
            playBtn.innerHTML = 'Prikazi stranicu';
            playBtn.setAttribute('data-editorId', editor.id);
            playBtn.setAttribute('class', 'editor-play');
            playBtn.addEventListener('click', function(e) {
                var editorsId = e.currentTarget.dataset.editorid;
                var editor = editorArray.find(e => e.id == editorsId);

                var htmlData = editor.htmlEditor.getValue();

                if (editor.data.hasOwnProperty('css')) {
                    var cssBlob = new Blob(["" + editor.cssEditor.getValue()], {type: "text/css"});
                    htmlData = htmlData.replaceAll(editor.data["css"].name, URL.createObjectURL(cssBlob));

                }
                
                if (editor.data.hasOwnProperty('js')) {
                    var jsBlob = new Blob(["" + editor.jsEditor.getValue()], {type: "text/javascript"});
                    htmlData = htmlData.replaceAll(editor.data["js"].name, URL.createObjectURL(jsBlob));

                }


                var htmlBlob = new  Blob(["" + htmlData], {type: "text/html"});
                var htmlURL = URL.createObjectURL(htmlBlob);

                if(!document.getElementById(editor.id + "-iframe")) {
                var htmliframe = document.createElement('iframe');
                htmliframe.setAttribute('style', 'width: calc(50% - 3px); height: 330px; display: none;');
                htmliframe.setAttribute('id', editor.id + "-iframe");
                document.getElementById(editor.id).append(htmliframe);
                } else {
                    document.getElementById(editor.id + "-iframe").style.display = 'block';
                }
                
                document.getElementById(editor.id + "-iframe").setAttribute('src', htmlURL);

                

            });


            var downloadBtn = document.createElement('div');
            downloadBtn.innerHTML = 'Preuzmi fileove';
            downloadBtn.setAttribute('data-editorId', editor.id);
            downloadBtn.setAttribute('class', 'editor-play');
            downloadBtn.addEventListener('click', function(e) {
                var editorsId = e.currentTarget.dataset.editorid;
                var editor = editorArray.find(e => e.id == editorsId);

                var zip = new JSZip();

                zip.file(editor.data["html"].name, editor.htmlEditor.getValue());
                zip.file(editor.data["js"].name, editor.jsEditor.getValue());
                zip.file(editor.data["css"].name , editor.cssEditor.getValue());


                zip.generateAsync({type:"base64"}).then(function (content) {
                    var link = document.createElement('a');
                    link.href = "data:application/zip;base64," + content;
                    link.download = "petlja-files.zip";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
               });

                

            });
            var btnDiv = document.createElement('div');
            btnDiv.append(playBtn);
            btnDiv.append(downloadBtn)
            btnDiv.setAttribute('class', 'editor-btn');
            document.getElementById(editor.id).append(btnDiv);
        });


    });
}
WrappingAscorinaion();