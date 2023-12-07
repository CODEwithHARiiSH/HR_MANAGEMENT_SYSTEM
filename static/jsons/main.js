
function gotEmployees(data) {
    console.log(data);
    $("span.info")[0].innerHTML = "Loaded";
    $("#userdetails")[0].innerHTML = `<h1> Details for ${data.fname}  ${data.lname}</h1>
    <h2> ${data.title} </h2>
    <table>
      <tr>
        <th> First name </th>
        <td> ${data.fname}</td>
      </tr>
      <tr>
        <th> Last name </th>
        <td> ${data.lname}</td>
      </tr>
      <tr>
        <th> Email </th>
        <td> ${data.email}</td>
      </tr>

      <tr>
        <th> Phone </th>
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
            ${renderNavigationButtons(data)}
`;

}

function renderNavigationButtons(data) {
    if (data.id === data.last_id) {
        return `<button> <a href="{{url_for('api_employee_details', empid=${data.id + 1})}}">Next</a></button>`;
        } else {
            return `
                <button> <a href="{{url_for('api_employee_details','empid'= ${data.id - 1 })}}">Previous</a></button>
                <button> <a href="{{url_for('api_employee_details', empid=${data.id + 1})}}">Next</a></button>
            `;
        }
}

$(function () {
    $("a.userlink").click(function (ev) {
        $("span.info")[0].innerHTML = "Loading...";
        $.get(ev.target.href, gotEmployees);
        ev.preventDefault();
    });
});

