<template>
    <v-container> 
      <v-card> 
        <v-card-title>Admin Panel</v-card-title> 
        <v-btn color="red" @click="logout" class="ma-2">Logout</v-btn> 
        <v-table> 
          <thead> 
            <tr> 
              <th>Name</th> 
              <th>Description</th> 
              <th>Actions</th> 
            </tr> 
          </thead> 
          <tbody> 
            <tr v-for="item in items" :key="item.id"> 
              <td>{{ item.name }}</td> 
              <td>{{ item.description }}</td> 
              <td> 
                <v-btn color="red" @click="deleteItem(item.id)">Delete</v-btn> 
              </td> 
            </tr> 
          </tbody> 
        </v-table> 
      </v-card> 
    </v-container> 
</template> 
  
<script> 
  import { mapActions, mapState } from 'vuex'; 
  import axios from 'axios'; 
  
  export default { 
    data() { 
      return { items: [] }; 
    }, 
    computed: { 
      ...mapState(['token']), 
    }, 
    async created() { 
      const response = await axios.get('http://127.0.0.1:8000/api/items/', { 
        headers: { Authorization: `Bearer ${this.token}` }, 
      }); 
      this.items = response.data; 
    }, 
    methods: { 
      ...mapActions(['logout']), 
      async deleteItem(id) { 
        await axios.delete(`http://127.0.0.1:8000/api/items/${id}/`, { 
          headers: { Authorization: `Bearer ${this.token}` }, 
        }); 
        this.items = this.items.filter(item => item.id !== id); 
      }, 
    }, 
  }; 
</script>