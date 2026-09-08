import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Simulator from '../views/Simulator.vue'
import History from '../views/History.vue'
import Profile from '../views/Profile.vue'
import Login from '../views/Login.vue'

import AlgorithmDetails from '../views/AlgorithmDetails.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/simulator', component: Simulator },
  { path: '/algorithms/:id', component: AlgorithmDetails },
  { path: '/history', component: History },
  { path: '/profile', component: Profile },
  { path: '/login', component: Login }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
