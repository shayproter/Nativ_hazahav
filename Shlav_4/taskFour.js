//4
import React, { useState, useEffect } from 'react';
import './App.css';

function canPlanTakeOff(response) {
	if (response.can_plane_takeoff) {
		return (<p> Plane can take off<br/>Possible departure hours:
            <ul>
				{response.hours_for_takeoff.map((hour, index) => (<li key={index}>{hour}</li>
				))}
			</ul></p>)
	} else {
		return (<p>Plane cannot take off, average temperature is {response.temp}</p>)
	}	
}

function App() {
  const [input, setInput] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [response, setResponse] = useState(null);

  const handleSubmit = async event => {
    event.preventDefault();
    setSubmitted(true);

    const response = await fetch('http://127.0.0.1:5000', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cargo_mass: parseInt(input) })
    });

    const result = await response.json();
    setResponse(result);
  };

  return (
    <div>
      <header className="App-header">
        <p>
          Welcome to my Physical calculator, Please enter the mass of the cargo your carrying
        </p>
        <form onSubmit={handleSubmit}>
          <label>
            Input:
            <input type="text" value={input} onChange={event => setInput(event.target.value)} />
          </label>
          <button type="submit">Submit</button>
        </form> //checking for wrong input error
		{response && !response.message && (
			<div>
				<p> Input is wrong, Please try again </p>
			</div>
		)}

        {response && response.message && (
          <div>
            <p>Distance till take-off: {response.flight_statistics.distance_till_take_off}</p>
            <p>Time till take-off: {response.flight_statistics.time_till_take_off}</p>
            {response.flight_statistics.cargo_mass_to_lose && <p>Cargo mass to lose: {response.flight_statistics.cargo_mass_to_lose}</p>}
			{canPlanTakeOff(response)}	
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
