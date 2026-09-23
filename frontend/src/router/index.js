/**
 * Application routes.
 *
 *   /                  Home (hero + live cipher-tape demo)
 *   /learn             Guided 5-station learning path for beginners
 *   /simulator         Simulation bench; accepts ?algo=<id> to preselect
 *                      (used by the "try it" button on reference pages)
 *   /algorithms/:id    Bilingual reference guide per algorithm
 *   /history           JWT-protected simulation history
 *   /profile           Account info · /login  Auth (login/register tabs)
 */
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import LearnPath from '../views/LearnPath.vue'
import Simulator from '../views/Simulator.vue'
import History from '../views/History.vue'
import Profile from '../views/Profile.vue'
import Login from '../views/Login.vue'

import AlgorithmDetails from '../views/AlgorithmDetails.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/learn', component: LearnPath },
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
