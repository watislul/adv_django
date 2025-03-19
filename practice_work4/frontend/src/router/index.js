import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue'; 
import Admin from '../views/Admin.vue'; 
import store from '../store'; 
import Register from '../views/Register.vue'; 
 
const routes = [ 
    { path: '/', component: Login }, 
    {  
        path: '/admin', 
        component: Admin, 
        meta: { requiresAdmin: true }, 
    }, 
    { path: '/register', component: Register },
]; 
 
const router = createRouter({ history: createWebHistory(), routes }); 
 
router.beforeEach(async (to, from, next) => { 
    if (to.meta.requiresAdmin) { 
        await store.dispatch('fetchUser'); 
        if (store.state.user?.role === 'admin') { 
            next(); 
        } else { 
            next('/'); 
        } 
    } else { 
        next(); 
    } 
});



export default router; 