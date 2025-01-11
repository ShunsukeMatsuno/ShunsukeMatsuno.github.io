window.onload = function () {
  replaceExpandableContent();

  var elements = document.querySelectorAll("div.expand");
  elements.forEach(function (el) {
    var previousElement = el.previousElementSibling;
    previousElement.innerHTML += '<br>&nbsp;&nbsp;&nbsp;<span> <a href="#" class="expand-link">+ Abstract</a></span>';
  });

  var expandLinks = document.querySelectorAll(".expand-link");
  expandLinks.forEach(function (link) {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      var expandableDiv = this.parentNode.parentNode.nextElementSibling;
      var collapseBtn = expandableDiv.querySelector(".collapse-btn");
      var isExpanded = expandableDiv.classList.toggle('expanded');

      this.innerText = isExpanded ? "− Abstract" : "+ Abstract";
      collapseBtn.style.display = isExpanded ? "inline-block" : "none";
    });
  });
};

function replaceExpandableContent() {
  var expandContentDivs = document.querySelectorAll("div#ExpandContent");
  expandContentDivs.forEach(function (expandContentDiv) {
    var content = expandContentDiv.innerHTML;
    content = content.replace(/<p>\[expand\]<\/p>/g, "").replace(/<p>\[\/expand\]<\/p>/g, "");
    var parentcontent = `<div class="expand">${content}</div>`;
    expandContentDiv.outerHTML = parentcontent;
  });
}