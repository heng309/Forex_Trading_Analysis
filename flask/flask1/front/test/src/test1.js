import React, { useState, useEffect } from 'react';
import axios from 'axios';




const App = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/data')
      .then(res => {
        setData(res.data.data);
      }) ; 
  }, []);



  return (
  <h1> test :  {data[0].name}  </h1>
);
};

export default App;

