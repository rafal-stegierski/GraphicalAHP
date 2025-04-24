import axios from 'axios';

axios.defaults.baseURL = 'http://207.154.241.50:8000';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

export default axios;
