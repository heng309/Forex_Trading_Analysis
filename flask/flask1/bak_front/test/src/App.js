import React, { useState, useEffect } from 'react';
import axios from 'axios';



const App = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/data')
    .then(response => {
        setData(response.data.data);
        setLoading(false);
      })
      .catch(err => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
  <h2> test :  {data[0].name} {data[0].age }  </h2>
);
};

export default App;
