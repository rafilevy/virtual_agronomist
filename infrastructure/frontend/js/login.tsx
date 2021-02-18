import React from 'react';
import ReactDOM from 'react-dom';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import TextField from '@material-ui/core/TextField';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';


const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
  error: {
    fontSize: "14px",
    fontWeight: 700,
    display: "block",
    padding: "10px 12px",
    margin: "20px 0px 10px 0px",
    color: "#ba2121",
    border: "1px solid #ba2121",
    borderRadius: "4px",
    backgroundColor: "#fff",
    backgroundPosition: "5px 12px",
  }
}));

interface Dictionary {
    [Key: string]: any;
}

declare var CSRFTOKEN: string;
declare var FORM_ERRORS: Dictionary;

function SignIn() {
  const classes = useStyles();

  var message = undefined;
  if (FORM_ERRORS["__all__"] && FORM_ERRORS["__all__"].length > 0) {
    message = FORM_ERRORS["__all__"][0]["message"];
  }
  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <div className={classes.paper}>
        <Avatar className={classes.avatar}>
          <LockOutlinedIcon />
        </Avatar>
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
        {message && <p className={classes.error}>{message}</p>}
        <form className={classes.form} method="post">
        <input type="hidden" name="csrfmiddlewaretoken" value={CSRFTOKEN} />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="username"
            label="Email Address"
            name="username"
            autoComplete="email"
            autoFocus
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
          >
            Sign In
          </Button>
        </form>
      </div>
    </Container>
  );
}

ReactDOM.render(
    <React.StrictMode>
      <SignIn />
    </React.StrictMode>,
    document.getElementById('root')
  );
  