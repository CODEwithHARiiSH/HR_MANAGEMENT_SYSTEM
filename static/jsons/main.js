function GotEmployees({ data }) {
  return (
    <div>
      <h1>{data.fname} {data.lname}</h1>
      <h5>Designation: {data.title}</h5>
      <div>
        <strong>First name:</strong> {data.fname}<br />
        <strong>Last name:</strong> {data.lname}<br />
        <strong>Email:</strong> {data.email}<br />
        <strong>Phone:</strong> {data.phone}<br />
      </div>
      <div>
        <strong>Leave taken:</strong> {data.leave}<br />
        <strong>Maximum leave allowed:</strong> {data.max_leave}<br />
        <strong>Remaining leaves:</strong> {data.max_leave - data.leave}<br />
      </div>
      <br />
      <br />
    </div>
  );
}

function EmployeeDetails({ empId }) {
  const [employeeData, setEmployeeData] = React.useState(null);

  React.useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(`/employees/${empId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setEmployeeData(data);
      } catch (error) {
        console.error('Error fetching employee details:', error);
        setEmployeeData(null);
      }
    }

    fetchData();
  }, [empId]);

  return (
    <div>
      {employeeData ? (
        <GotEmployees data={employeeData} />
      ) : (
        <span>Loading employee data...</span>
      )}
    </div>
  );
}


// function App({ empId }) {
//   return (
//     <div>
//       <EmployeeDetails empId={empId} />
//     </div>
//   );
// }

function App({ empId }) {
  const [currentEmpId, setCurrentEmpId] = React.useState(empId);
  const [employeeIds, setEmployeeIds] = React.useState([]);
  const [currentIndex, setCurrentIndex] = React.useState(0);

  React.useEffect(() => {
    async function fetchIds() {
      try {
        const response = await fetch(`/ids`);
        const ids = await response.json();
        setEmployeeIds(ids);
        const initialIndex = ids.findIndex(emp => emp.id === empId);
        setCurrentIndex(initialIndex !== -1 ? initialIndex : 0);
      } catch (error) {
        console.error('Error fetching employee IDs:', error);
      }
    }

    fetchIds();
  }, [empId]);
  const handleNextButtonClick = () => {
    setCurrentIndex((prevIndex) => Math.min(prevIndex + 1, employeeIds.length - 1));
    if (currentIndex === employeeIds.length-1){
      setCurrentEmpId(employeeIds[currentIndex].id);
    }
    else {
      setCurrentEmpId(employeeIds[currentIndex + 1].id);
    }
  };

  const handlePreviousButtonClick = () => {
    setCurrentIndex((prevIndex) => Math.max(prevIndex - 1, 0));
    if (currentIndex === 0){
      setCurrentEmpId(employeeIds[currentIndex].id);
    }
    else{
      setCurrentEmpId(employeeIds[currentIndex - 1].id);
    }
  };
  return (
    <div>
      <EmployeeDetails empId={currentEmpId} />
      <button onClick={handlePreviousButtonClick}>&#8666;</button>
      <button onClick={handleNextButtonClick}>  &#8667;</button>
    </div>
  );
}

function handleEmployeeClick(empId) {
  ReactDOM.render(<App empId={empId} />, document.getElementById('userdetails'));
}