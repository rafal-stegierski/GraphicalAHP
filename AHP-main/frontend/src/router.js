import axios from './axiosConfig.js';
import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from './components/MainLayout.vue';
//import MainComponent from './components/MainComponent.vue';
import UserLogin from './components/UserLogin.vue';
//import UserRegister from './components/UserRegister.vue';
//import ValidateToken from './components/ValidateToken.vue';
//import ForgotPassword from './components/ForgotPassword.vue';
//import ResetPassword from './components/ResetPassword.vue';
import CreateSurveyComponent from './components/CreateSurveyComponent.vue'; 
//import FillSurveyComponent from './components/FillSurveyComponent.vue'; 
import SurveyListComponent from './components/SurveyListComponent.vue';
import MainDashboard from './components/MainDashboard.vue';
import AHPLoaderComponent from './components/AHPLoaderComponent.vue';
//import ResultsPage from './components/ResultsPage.vue';

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: 'dashboard', component: MainDashboard },
      { path: 'login', component: UserLogin },
      //{ path: 'register', component: UserRegister },
      //{ path: 'validate-token', component: ValidateToken },
      //{ path: 'forgot-password', component: ForgotPassword },
      //{ path: 'reset-password', component: ResetPassword },
      //{ path: 'main', component: MainComponent },
      { path: 'create-survey', component: CreateSurveyComponent, meta: { requiresAuth: true } },
      // { path: 'fill-survey/:id', component: FillSurveyComponent },
      { path: 'fill-survey', component: AHPLoaderComponent },
      { path: 'survey-list', component: SurveyListComponent, meta: { requiresAuth: true } },
      { path: 'ahploader', component: AHPLoaderComponent },
      { path: '', redirect: '/dashboard' }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token');

    if (!token) {
      return next('/login'); // Brak tokena -> przekierowanie
    }

    axios.get('/api/checkToken', {
      headers: { Authorization: `Bearer ${token}` } // Przekazanie tokena w nagłówku
    })
    .then(() => next()) // Token poprawny -> przejście
    .catch(() => next('/login')); // Token niepoprawny -> przekierowanie do logowania
  } else {
    next(); // Nie wymaga autoryzacji -> pozwól nawigować
  }
});


export default router;
