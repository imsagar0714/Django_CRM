from django.views import generic
import random
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from leads.models import Agent
from .forms import AgentModelform
from .mixins import OrganiserAndLoginRequiredMixin
from django.core.mail import send_mail

class AgentListView(OrganiserAndLoginRequiredMixin,generic.ListView):
    template_name="agents/agents_list.html"
    
    def get_queryset(self):
        organisation=self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)

class AgentCreateView(OrganiserAndLoginRequiredMixin,generic.CreateView):
    template_name="agents/agents_create.html"
    form_class=AgentModelform
    
    def get_success_url(self):
        return reverse("agents:agents-list")
    
    def form_valid(self, form):
        user=form.save(commit=False)
        user.is_agent=True
        user.is_organiser=False
        user.set_password(f"{random.randint(0,10000)}")
        user.save()
        Agent.objects.create(
            user=user,
            organisation=self.request.user.userprofile
        )
        send_mail(
            subject="you are invited to be an agent",
            message="you were added as an agent in djcrm. please login to start working",
            from_email="admin@gmail.com",
            recipient_list=[user.email]
        )
        return super(AgentCreateView,self).form_valid(form)
    
class AgentUpdateView(OrganiserAndLoginRequiredMixin,generic.UpdateView):
    template_name="agents/agents_update.html"
    form_class=AgentModelform
    
    def get_success_url(self):
        return reverse("agents:agents-list")
    
    def get_queryset(self):
        organisation=self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)

    
class AgentDetailView(OrganiserAndLoginRequiredMixin,generic.DetailView):
    template_name="agents/agents_detail.html"
    context_object_name="agent"
    
    def get_queryset(self):
        organisation=self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)
    
class AgentDeleteView(OrganiserAndLoginRequiredMixin,generic.DeleteView):
    template_name="agents/agents_delete.html"
    context_object_name="agent"
    
    def get_success_url(self):
        return reverse("agents:agents-list")
    
    def get_queryset(self):
        organisation=self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)