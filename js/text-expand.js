window.onload = function() {
    replaceExpandableContent();

    var elements = document.querySelectorAll('div.expand');
    Array.prototype.forEach.call(elements, function(el, i){
        el.previousElementSibling.innerHTML = el.previousElementSibling.innerHTML + '<br>&nbsp;&nbsp;&nbsp<span class="abstract-button" style="margin-top: 0px;"> <a href="#" class="expand-link" style="cursor: pointer; display: inline-block;"> +Abstract</a></span>';
    });

    var expandLinks = document.querySelectorAll('.expand-link');
    Array.prototype.forEach.call(expandLinks, function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            var expandableDiv = this.parentNode.parentNode.nextElementSibling;
            var collapseBtn = expandableDiv.querySelector('.collapse-btn');
            if (expandableDiv.style.display === 'none') {
                expandableDiv.style.display = 'block';
                expandableDiv.style.height = 'auto';
                if (!collapseBtn) {
                    collapseBtn = document.createElement('button');
                    collapseBtn.innerText = 'c';
                    collapseBtn.className = 'collapse-btn';
                    collapseBtn.style.cursor = 'pointer';
                    collapseBtn.style.backgroundColor = 'transparent'; // Match the background color of the link
                    collapseBtn.style.border = 'none'; // Remove button border
                    //collapseBtn.style.textDecoration = 'underline'; // Underline the button text
                    collapseBtn.style.marginLeft = '5px'; // Adjust the margin as needed
                    collapseBtn.style.marginTop = '-10px'; // Adjust the margin as needed
                    collapseBtn.onclick = function() {
                        expandableDiv.style.display = 'none';
                        link.style.display = 'inline-block';
                        collapseBtn.style.display = 'none';
                    };
                    this.parentNode.replaceChild(collapseBtn);
                } else {
                    collapseBtn.style.display = 'inline-block';
                }
            } else {
                expandableDiv.style.display = 'none';
                if (collapseBtn) {
                    collapseBtn.style.display = 'none';
                }
            }
        });
    });
};

function replaceExpandableContent() {
    var expandContentDivs = document.querySelectorAll('div#ExpandContent');
    Array.prototype.forEach.call(expandContentDivs, function(expandContentDiv) {
        var content = expandContentDiv.innerHTML;
        content = content.replace(/<p>\[expand\]<\/p>/g, '').replace(/<p>\[\/expand\]<\/p>/g, '');
        var parentcontent = '<div class="expand" style="display: none; height: 0; overflow: hidden; margin-left: 40px;  margin-top: -40px;">' + content + '</div>';
        expandContentDiv.outerHTML = parentcontent;
    });
}
