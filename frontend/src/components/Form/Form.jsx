import React, { useState } from 'react';
import { Grid, TextField, Button, CircularProgress } from '@mui/material';
import axios from 'axios';


const Form = () => {
 const [post, setPost] = useState('');
 const [image, setImage] = useState('');


 const handleInput = (event) => {
   setPost(event.target.value);
 };


 const handleSubmit = async (event) => {
  console.log(1);
   event.preventDefault();
   await axios.post('http://127.0.0.1:5000', {
     message: post,
   })
     .then((response) => {
      console.log(response);
       setImage(response.data);
     })
     .catch((error) => {
       console.log(error);
     });
 };
 return (
   <div>
     <form onSubmit={handleSubmit}>
       <Grid container spacing={1}>
         <Grid item xs={12}>
           <TextField onChange={handleInput} label="How was your day?" multiline rows={15} placeholder="Type your message here" variant="outlined" fullWidth required />
         </Grid>
         <Grid item xs={12}>
           <Button type="generate" variant="contained" color="primary" fullWidth>Submit</Button>
         </Grid>
       </Grid>
     </form>
     {image
       ? (
         <Grid container spacing={1}>
           <Grid item xs={12}>
             <img src={image} alt="mood" />
           </Grid>
         </Grid>
       )
       : (
         <Grid paddingTop="50px" justifyContent="center">
           <CircularProgress />
         </Grid>
       )}
   </div>
 );
};


export default Form;


