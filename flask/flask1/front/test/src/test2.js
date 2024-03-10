import React, { useState, useEffect } from 'react';
import axios from 'axios';

 const INITIAL_STATE = {
   email: '',
   password: '',
 };


const App = () => {
  const [data, setData] = useState([]);
  const [plot, setPlot] = useState([]);
  const [plot1, setPlot1] = useState("https://raw.githubusercontent.com/mdn/learning-area/master/html/multimedia-and-embedding/images-in-html/dinosaur_small.jpg") ; 
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState([]); 
  const [form, setForm] = React.useState(INITIAL_STATE);

  useEffect(() => {
    axios.get('/data')
    .then(response => {
        setData(response.data.data);
        setLoading(false);
      })
      .catch(err => {
        setLoading(false);
      });

    axios.get('/plot')
    .then(response => {
        setPlot(response.data.plot);
        setLoading(false);
         console.log( plot ) ; 
      })
      .catch(err => {
        setLoading(false);
      });



  }, []);


  const handleSubmit = (event) => {
    event.preventDefault();
    setForm(INITIAL_STATE);
    setPlot1( `data:image/png;base64,${plot}` ) ; 
  };
  
  const handleChange = (event) => {
    setForm({
      ...form,
      [event.target.id]: event.target.value,
    });
  };


  if (loading) {
    return <div>Loading...</div>;
  }

  return (

<body>


<div>
  <p> test :  {data[0].name} {data[0].age }  </p>
<figure>
  <img
    src = {`data:image/png;base64,${plot}`}
    alt="一只恐龙头部和躯干的骨架，它有一个巨大的头，长着锋利的牙齿。"
   // width="400"
   // height="341" 
  />
  <figcaption>曼彻斯特大学博物馆展出的一只霸王龙的化石</figcaption>
</figure>
</div>


<div>
<form onSubmit={handleSubmit} >
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="text" value = {form.email}  
                   onChange={handleChange}
       />
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" value = {form.password} 
          onChange={handleChange}
       />
      </div>
      <button>Submit</button>
    </form>

</div>

<div>
<p>   email : {form.email} </p>
<p>   email : {form.password} </p>
</div>


<div>
<figure>
  <img
    src = {plot1}
    alt="一只恐龙头部和躯干的骨架，它有一个巨大的头，长着锋利的牙齿。"
   // width="400"
   // height="341" 
  />
  <figcaption>曼彻斯特大学博物馆展出的一只霸王龙的化石</figcaption>
</figure>
</div>




</body>

);
};

export default App;
