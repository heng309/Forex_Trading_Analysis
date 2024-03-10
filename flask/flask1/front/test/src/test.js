// react part 
import React, { useState, useEffect } from 'react';
import axios from 'axios'


function App() {
const [joke, setJoke] = useState(null);
  useEffect(() => {
  axios.get('http://127.0.0.1:5000/data')
  .then(function (response) {
    console.log(response.data.data[0].name);
    setJoke( response.data.data[0].name ) ;
     
  })
  .catch(function (error) {
    console.log(error);
  });

  }, []);
  return (
    <div>
      <h2>Joke of the day: </h2>
       {joke}
    </div>
  );
};


export default App;
