$(function () {
  $("a.userlink").click(function (ev) {
      $("span.info")[0].innerHTML = "&#9992; .... &#9992; .... &#9992; .... &#9992;....";
      $.get(ev.target.href, gotEmployees);
      ev.preventDefault();
  });
});

function gotEmployees(data , msg) {
  console.log(msg);
    console.log(data);
    $("span.info")[0].innerHTML = "Done &#9745;";
    $("div#userdetails").data("empid", data.id);
    $("#userdetails")[0].innerHTML = `<h1> ${data.fname}  ${data.lname}</h1>
    <hr>
    <h5>Designation :  ${data.title} </h5>
    <table>
      <tr>
        <th> First name :</th>
        <td> ${data.fname}</td>
      </tr>
      <tr>
        <th> Last name :</th>
        <td> ${data.lname}</td>
      </tr>
      <tr>
        <th> Email :</th>
        <td> ${data.email}</td>
      </tr>

      <tr>
        <th> Phone :</th>
        <td> ${data.phone}</td>
      </tr>
      </table>
      <hr>
      <h2 style="text-align: center;"> Leave details</h2>
          <table>
              <tr>
                <th> Leave taken :</th>
                <td> ${data.leave}</td>
              </tr>
              <tr>
                <th> Maximum leave allowed :</th>
                <td> ${data.max_leave}</td>
              </tr>
              <tr>
                <th> Remaining leaves :</th>
                <td> ${data.max_leave - data.leave}</td>
              </tr>
            </table>
            <hr>
            <br>
            ${renderForm(data)}
`;

}

// function for generate form

 function renderForm(data){
if (data.max_leave === data.leave){
  return `
  <div class="danger-messages">
  <div class="danger-message">
  Adding Leave is blocked , ${data.fname} has taken maximum allowed leaves
  </div>
  </div>`;
}
else {
  return `<form action="/add_leaves/${data.id}" method="post">

  <input type="date" id="date" name="date" placeholder="Date" ><br>
  <textarea id="reason" name="reason" rows="4" cols="50" placeholder="Reason" ></textarea><br>

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
    const currentEmpId = parseInt($("div#userdetails").data("empid"));
    const nextEmpId = direction === 'next' ? currentEmpId + 1 : currentEmpId - 1;
    getEmployeeDetails(nextEmpId);
}

function onNextButtonClick() {
    navigateEmployee('next');
}
  ``
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
  if (button1.style.display === "none")
       {button1.style.display = "block";
       button2.style.display = "block";}
}

function changeButtonAndHighlight(link) {
  changeButtonStyle();
  highlightUser(link);
}