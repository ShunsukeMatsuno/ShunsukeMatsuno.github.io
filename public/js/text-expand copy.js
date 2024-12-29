window.onload = function () {
  replaceExpandableContent();

  var elements = document.querySelectorAll("div.expand");
  Array.prototype.forEach.call(elements, function (el, i) {
    el.previousElementSibling.innerHTML =
      el.previousElementSibling.innerHTML +
      '<br>&nbsp;&nbsp;&nbsp;<span> <a href="#" class="expand-link">+ Abstract</a></span>';
  });

  var expandLinks = document.querySelectorAll(".expand-link");
  Array.prototype.forEach.call(expandLinks, function (link) {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      var expandableDiv = this.parentNode.parentNode.nextElementSibling;
      var collapseBtn = expandableDiv.querySelector(".collapse-btn");
      if (expandableDiv.style.display === "none") {
        expandableDiv.style.display = "block";
        expandableDiv.style.height = "auto";
        this.innerText = "− Abstract"; // Change button text to "- Abstract" when expanded
        collapseBtn.style.display = "inline-block";
      } else {
        expandableDiv.style.display = "none";
        this.innerText = "+ Abstract"; // Change button text back to "+ Abstract" when collapsed
      }
    });
  });
};

function replaceExpandableContent() {
  var expandContentDivs = document.querySelectorAll("div#ExpandContent");
  Array.prototype.forEach.call(expandContentDivs, function (expandContentDiv) {
    var content = expandContentDiv.innerHTML;
    content = content
      .replace(/<p>\[expand\]<\/p>/g, "")
      .replace(/<p>\[\/expand\]<\/p>/g, "");
    var parentcontent =
      '<div class="expand" style="display: none; height: 0; overflow: hidden; margin-left: 20px;  margin-top: -35px">' +
      content +
      "</div>";
    expandContentDiv.outerHTML = parentcontent;
  });
}
