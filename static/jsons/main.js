$(function () {
  $("a.userlink").click(function (ev) {
      $.get(ev.target.href, gotEmployees);
      $("span.info")[0].innerHTML = "&#9992; .... &#9992; .... &#9992; .... &#9992;....";
      ev.preventDefault();
  });
});

function gotEmployees(data) {
    console.log(data)
    $("span.info")[0].innerHTML = "Done &#9745;";
    $("div#userdetails").data("empid", data.id);
    $("#userdetails")[0].innerHTML = `
        <h1>${data.fname} ${data.lname}</h1>
        <h5>Designation: ${data.title}</h5>
        <hr>
        <div>
            <strong>First name:</strong> ${data.fname}<br>
            <strong>Last name:</strong> ${data.lname}<br>
            <strong>Email:</strong> ${data.email}<br>
            <strong>Phone:</strong> ${data.phone}<br>
        </div>
        <hr>
        <h2 style="text-align: center;">Leave details</h2>
        <div>
            <strong>Leave taken:</strong> ${data.leave}<br>
            <strong>Maximum leave allowed:</strong> ${data.max_leave}<br>
            <strong>Remaining leaves:</strong> ${data.max_leave - data.leave}<br>
        </div>
        <hr>
        <br>
        ${renderForm(data)}
`;

}

// function for generate form

 function renderForm(data){
if (data.max_leave === data.leave){
  return `
  <h5>&#9888; Adding Leave is blocked , ${data.fname} has taken maximum allowed leaves</h5>
 `;
}
else {
  return `<form action="/add_leaves/${data.id}" method="post">

  <input type="date" id="date" name="date" placeholder="Date" ><br>
  <textarea id="reason" name="reason" rows="4" cols="30" placeholder="Reason" ></textarea><br>

  <div class="col-auto">
    <button type="submit" class="btn btn-primary mb-3">Submit</button>
  </div>
  </form>` ;
  }
}
 
// functions for next and previous buttons

function getEmployeeDetails(empid) {
    $.get(`/employees/${empid}`, gotEmployees);
}

function navigateEmployee(direction) {
  $("span.info")[0].innerHTML = "&#9992; .... &#9992; .... &#9992; .... &#9992;....";
  const currentEmpId = parseInt($("div#userdetails").data("empid"));                  //get current employee id
  const userLinks = document.querySelectorAll('.userlink');
  $.get(`/ids`, function (data) {                                                    //get array of id from api
    let ids = data
    if (ids.length > 0) {
      const currentIndex = ids.findIndex(emp => emp.id === currentEmpId);            //checks for current id if there put one
      const nextIndex = direction === 'next' ? currentIndex + 1 : currentIndex - 1;
      if (nextIndex >= 0 && nextIndex < ids.length) {
        const nextEmpId = ids[nextIndex].id;
        highlightUser(userLinks[nextIndex]);
        getEmployeeDetails(nextEmpId);
      } else {
        console.log('Cannot navigate further in the specified direction.');
        $("span.info")[0].innerHTML = "&#9888;Cannot navigate further in the specified direction.";
      }
    } else {
      console.log('No employees data available.');
      $("span.info")[0].innerHTML = "No employees data available.";
    }
  })
}


function onNextButtonClick() {
    navigateEmployee('next');
}
function onPreviousButtonClick() {
    navigateEmployee('previous');
}

$(function () {
    $("button#next").click(onNextButtonClick);
    $("button#pre").click(onPreviousButtonClick);
});

function highlightUser(link) {
  var userLinks = document.querySelectorAll('.userlink');
  userLinks.forEach(function(userLink) {
      userLink.classList.remove('highlighted');
  });
  link.classList.add('highlighted');
}
function changeButtonStyle() {
  var button1 = document.getElementById("next");
  var button2 = document.getElementById("pre");

  if (button1.style.display === "none")  {
      button1.style.display = "block";
      button2.style.display = "block";
    }
  }

function changeButtonAndHighlight(link) {
  changeButtonStyle();
  highlightUser(link);}